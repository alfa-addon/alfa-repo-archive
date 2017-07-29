# -*- coding: utf-8 -*-

try:
    from python_libtorrent import get_libtorrent, get_platform

    lt = get_libtorrent()
except Exception, e:
    import libtorrent as lt

import os
import pickle
import random
import time
import urllib

from cache import Cache
from core import logger
from dispatcher import Dispatcher
from file import File
from handler import Handler
from monitor import Monitor
from resume_data import ResumeData
from server import Server


class Client(object):
    INITIAL_TRACKERS = ['udp://tracker.openbittorrent.com:80',
                        'udp://tracker.istole.it:80',
                        'udp://open.demonii.com:80',
                        'udp://tracker.coppersurfer.tk:80',
                        'udp://tracker.leechers-paradise.org:6969',
                        'udp://exodus.desync.com:6969',
                        'udp://tracker.publicbt.com:80']

    VIDEO_EXTS = {'.avi': 'video/x-msvideo', '.mp4': 'video/mp4', '.mkv': 'video/x-matroska',
                  '.m4v': 'video/mp4', '.mov': 'video/quicktime', '.mpg': 'video/mpeg', '.ogv': 'video/ogg',
                  '.ogg': 'video/ogg', '.webm': 'video/webm', '.ts': 'video/mp2t', '.3gp': 'video/3gpp'}

    def __init__(self, url=None, port=None, ip=None, auto_shutdown=True, wait_time=20, timeout=5, auto_delete=True,
                 temp_path=None, is_playing_fnc=None, print_status=False):

        # server
        if port:
            self.port = port
        else:
            self.port = random.randint(8000, 8099)
        if ip:
            self.ip = ip
        else:
            self.ip = "127.0.0.1"
        self.server = Server((self.ip, self.port), Handler, client=self)

        # Options
        if temp_path:
            self.temp_path = temp_path
        else:
            self.temp_path = os.path.join(os.path.dirname(__file__), "tmp")
        self.is_playing_fnc = is_playing_fnc
        self.timeout = timeout
        self.auto_delete = auto_delete
        self.wait_time = wait_time
        self.auto_shutdown = auto_shutdown
        self.buffer_size = 15
        self.last_pieces_priorize = 5
        self.state_file = "state"
        self.torrent_paramss = {'save_path': self.temp_path, 'storage_mode': lt.storage_mode_t.storage_mode_sparse}

        # State
        self.has_meta = False
        self.meta = None
        self.start_time = None
        self.last_connect = 0
        self.connected = False
        self.closed = False
        self.file = None
        self.files = None
        self._th = None

        # Sesion
        self._cache = Cache(self.temp_path)
        self._ses = lt.session()
        self._ses.listen_on(0, 0)
        # Cargamos el archivo de estado (si esxiste)
        if os.path.exists(os.path.join(self.temp_path, self.state_file)):
            try:
                f = open(os.path.join(self.temp_path, self.state_file), "rb")
                state = pickle.load(f)
                self._ses.load_state(state)
                f.close()
            except:
                pass

        self._start_services()

        # Monitor & Dispatcher
        self._monitor = Monitor(self)
        if print_status:
            self._monitor.add_listener(self.print_status)
        self._monitor.add_listener(self._check_meta)
        self._monitor.add_listener(self.save_state)
        self._monitor.add_listener(self.priorize_start_file)
        self._monitor.add_listener(self.announce_torrent)

        if self.auto_shutdown:
            self._monitor.add_listener(self._auto_shutdown)

        self._dispatcher = Dispatcher(self)
        self._dispatcher.add_listener(self._update_ready_pieces)

        # Iniciamos la URL
        if url:
            self.start_url(url)

    def get_play_list(self):
        """
        Función encargada de generar el playlist
        """
        # Esperamos a lo metadatos
        while not self.has_meta:
            time.sleep(1)

        # Comprobamos que haya archivos de video
        if self.files:
            if len(self.files) > 1:
                return "http://" + self.ip + ":" + str(self.port) + "/playlist.pls"
            else:
                return "http://" + self.ip + ":" + str(self.port) + "/" + urllib.quote(self.files[0].path)

    def get_files(self):
        """
        Función encargada de genera el listado de archivos
        """
        # Esperamos a lo metadatos
        while not self.has_meta:
            time.sleep(1)
        files = []

        # Comprobamos que haya archivos de video
        if self.files:
            # Creamos el dict con los archivos
            for file in self.files:
                n = file.path
                u = "http://" + self.ip + ":" + str(self.port) + "/" + urllib.quote(n)
                s = file.size
                files.append({"name": n, "url": u, "size": s})

        return files

    def _find_files(self, files, search=None):
        """
        Función encargada de buscar los archivos reproducibles del torrent
        """
        # Obtenemos los archivos que la extension este en la lista
        videos = filter(lambda f: self.VIDEO_EXTS.has_key(os.path.splitext(f.path)[1]), files)

        if not videos:
            raise Exception('No video files in torrent')
        for v in videos:
            videos[videos.index(v)].index = files.index(v)
        return videos

    def set_file(self, f):
        """
        Función encargada de seleccionar el archivo que vamos a servir y por tanto, priorizar su descarga
        """
        # Seleccionamos el archivo que vamos a servir
        fmap = self.meta.map_file(f.index, 0, 1)
        self.file = File(f.path, self.temp_path, f.index, f.size, fmap, self.meta.piece_length(), self)
        self.prioritize_file()

    def prioritize_piece(self, pc, idx):
        """
        Función encargada de priorizar una determinada pieza
        """
        piece_duration = 1000
        min_deadline = 2000
        dl = idx * piece_duration + min_deadline
        self._th.set_piece_deadline(pc, dl, lt.deadline_flags.alert_when_available)

        if idx == 0:
            tail_pieces = 9
            # Piezas anteriores a la primera se desactivan
            if (self.file.last_piece - pc) > tail_pieces:
                for i in xrange(self.file.first_piece, pc):
                    self._th.piece_priority(i, 0)
                    self._th.reset_piece_deadline(i)

            # Piezas siguientes a la primera se activan
            for i in xrange(pc + 1, self.file.last_piece + 1):
                self._th.piece_priority(i, 1)

    def prioritize_file(self):
        """
        Función encargada de priorizar las piezas correspondientes al archivo seleccionado en la funcion set_file()
        """
        priorities = []
        for i in xrange(self.meta.num_pieces()):
            if i >= self.file.first_piece and i <= self.file.last_piece:
                priorities.append(1)
            else:
                priorities.append(0)
        self._th.prioritize_pieces(priorities)

    def download_torrent(self, url):
        """
        Función encargada de descargar un archivo .torrent
        """
        from core import scrapertools

        data = scrapertools.downloadpage(url)
        return data

    def start_url(self, uri):
        """
        Función encargada iniciar la descarga del torrent desde la url, permite:
          - Url apuntando a un .torrent
          - Url magnet
          - Archivo .torrent local
        """

        if self._th:
            raise Exception('Torrent is already started')

        if uri.startswith('http://') or uri.startswith('https://'):
            torrent_data = self.download_torrent(uri)
            info = lt.torrent_info(lt.bdecode(torrent_data))
            tp = {'ti': info}
            resume_data = self._cache.get_resume(info_hash=str(info.info_hash()))
            if resume_data:
                tp['resume_data'] = resume_data

        elif uri.startswith('magnet:'):
            tp = {'url': uri}
            resume_data = self._cache.get_resume(info_hash=Cache.hash_from_magnet(uri))
            if resume_data:
                tp['resume_data'] = resume_data

        elif os.path.isfile(uri):
            if os.access(uri, os.R_OK):
                info = lt.torrent_info(uri)
                tp = {'ti': info}
                resume_data = self._cache.get_resume(info_hash=str(info.info_hash()))
                if resume_data:
                    tp['resume_data'] = resume_data
            else:
                raise ValueError('Invalid torrent path %s' % uri)
        else:
            raise ValueError("Invalid torrent %s" % uri)

        tp.update(self.torrent_paramss)
        self._th = self._ses.add_torrent(tp)

        for tr in self.INITIAL_TRACKERS:
            self._th.add_tracker({'url': tr})

        self._th.set_sequential_download(True)
        self._th.force_reannounce()
        self._th.force_dht_announce()

        self._monitor.start()
        self._dispatcher.do_start(self._th, self._ses)
        self.server.run()

    def stop(self):
        """
        Función encargada de de detener el torrent y salir
        """
        self._dispatcher.stop()
        self._dispatcher.join()
        self._monitor.stop()
        self.server.stop()
        self._dispatcher.stop()
        if self._ses:
            self._ses.pause()
            if self._th:
                self.save_resume()
            self.save_state()
        self._stop_services()
        self._ses.remove_torrent(self._th, self.auto_delete)
        del self._ses
        self.closed = True

    def _start_services(self):
        """
        Función encargada de iniciar los servicios de libtorrent: dht, lsd, upnp, natpnp
        """
        self._ses.add_dht_router("router.bittorrent.com", 6881)
        self._ses.add_dht_router("router.bitcomet.com", 554)
        self._ses.add_dht_router("router.utorrent.com", 6881)
        self._ses.start_dht()
        self._ses.start_lsd()
        self._ses.start_upnp()
        self._ses.start_natpmp()

    def _stop_services(self):
        """
        Función encargada de detener los servicios de libtorrent: dht, lsd, upnp, natpnp
        """
        self._ses.stop_natpmp()
        self._ses.stop_upnp()
        self._ses.stop_lsd()
        self._ses.stop_dht()

    def save_resume(self):
        """
        Función encargada guardar los metadatos para continuar una descarga mas rapidamente
        """
        if self._th.need_save_resume_data() and self._th.is_valid() and self.meta:
            r = ResumeData(self)
            start = time.time()
            while (time.time() - start) <= 5:
                if r.data or r.failed:
                    break
                time.sleep(0.1)
            if r.data:
                self._cache.save_resume(self.unique_file_id, lt.bencode(r.data))

    @property
    def status(self):
        """
        Función encargada de devolver el estado del torrent
        """
        if self._th:
            s = self._th.status()
            # Download Rate
            s._download_rate = s.download_rate / 1000

            # Progreso del archivo
            if self.file:
                pieces = s.pieces[self.file.first_piece:self.file.last_piece]
                progress = float(sum(pieces)) / len(pieces)
            else:
                progress = 0

            s.progress_file = progress * 100

            # Tamaño del archivo
            if self.file:
                s.file_size = self.file.size / 1048576.0
            else:
                s.file_size = 0

            # Estado del buffer
            if self.file and self.file.cursor:  # Con una conexion activa: Disponible vs Posicion del reproductor
                percent = len(self.file.cursor.cache)
                percent = percent * 100 / self.buffer_size
                s.buffer = int(percent)

            elif self.file:  # Sin una conexion activa: Pre-buffer antes de iniciar
                # El Pre-buffer consta de dos partes_
                # 1. Buffer al inicio del archivo para que el reproductor empieze sin cortes
                # 2. Buffer al final del archivo (en algunos archivos el reproductor mira el final del archivo antes de comenzar)
                bp = []

                # El tamaño del buffer de inicio es el tamaño del buffer menos el tamaño del buffer del final
                first_pieces_priorize = self.buffer_size - self.last_pieces_priorize

                # Comprobamos que partes del buffer del inicio estan disponibles
                for x in range(first_pieces_priorize):
                    if self._th.have_piece(self.file.first_piece + x):
                        bp.append(True)
                    else:
                        bp.append(False)

                # Comprobamos que partes del buffer del final estan disponibles
                for x in range(self.last_pieces_priorize):
                    if self._th.have_piece(self.file.last_piece - x):
                        bp.append(True)
                    else:
                        bp.append(False)

                s.buffer = int(sum(bp) * 100 / self.buffer_size)

            else:  # Si no hay ningun archivo seleccionado: No hay buffer
                s.buffer = 0

            # Tiempo restante para cerrar en caso de tener el timeout activo
            if self.auto_shutdown:
                if self.connected:
                    if self.timeout:
                        s.timeout = int(self.timeout - (time.time() - self.last_connect - 1))
                        if self.file and self.file.cursor:
                            s.timeout = self.timeout
                        if s.timeout < 0: s.timeout = "Cerrando"
                    else:
                        s.timeout = "---"
                else:
                    if self.start_time and self.wait_time:
                        s.timeout = int(self.wait_time - (time.time() - self.start_time - 1))
                        if s.timeout < 0: s.timeout = "Cerrando"
                    else:
                        s.timeout = "---"

            else:
                s.timeout = "Off"

            # Estado de la descarga
            STATE_STR = ['En cola', 'Comprobando', 'Descargando metadata', \
                         'Descargando', 'Finalizado', 'Seeding', 'Allocating', 'Comprobando fastresume']
            s.str_state = STATE_STR[s.state]

            # Estado DHT
            if self._ses.dht_state() is not None:
                s.dht_state = "On"
                s.dht_nodes = self._ses.status().dht_nodes
            else:
                s.dht_state = "Off"
                s.dht_nodes = 0

            # Cantidad de Trackers
            s.trackers = len(self._th.trackers())

            # Origen de los peers
            s.dht_peers = 0
            s.trk_peers = 0
            s.pex_peers = 0
            s.lsd_peers = 0

            for peer in self._th.get_peer_info():
                if peer.source & 1:
                    s.trk_peers += 1
                if peer.source & 2:
                    s.dht_peers += 1
                if peer.source & 4:
                    s.pex_peers += 1
                if peer.source & 8:
                    s.lsd_peers += 1

            return s

    """
    Servicios:
      - Estas funciones se ejecutan de forma automatica cada x tiempo en otro Thread.
      - Estas funciones son ejecutadas mientras el torrent esta activo algunas pueden desactivarse 
        segun la configuracion como por ejemplo la escritura en el log
    """

    def _auto_shutdown(self, *args, **kwargs):
        """
        Servicio encargado de autoapagar el servidor
        """
        if self.file and self.file.cursor:
            self.last_connect = time.time()
            self.connected = True

        if self.is_playing_fnc and self.is_playing_fnc():
            self.last_connect = time.time()
            self.connected = True

        if self.auto_shutdown:
            # shudown por haber cerrado el reproductor
            if self.connected and self.is_playing_fnc and not self.is_playing_fnc():
                if time.time() - self.last_connect - 1 > self.timeout:
                    self.stop()

            # shutdown por no realizar ninguna conexion
            if (not self.file or not self.file.cursor) and self.start_time and self.wait_time and not self.connected:
                if time.time() - self.start_time - 1 > self.wait_time:
                    self.stop()

            # shutdown tras la ultima conexion
            if (not self.file or not self.file.cursor) and self.timeout and self.connected and not self.is_playing_fnc:
                if time.time() - self.last_connect - 1 > self.timeout:
                    self.stop()

    def announce_torrent(self):
        """
        Servicio encargado de anunciar el torrent
        """
        self._th.force_reannounce()
        self._th.force_dht_announce()

    def save_state(self):
        """
        Servicio encargado de guardar el estado
        """
        state = self._ses.save_state()
        f = open(os.path.join(self.temp_path, self.state_file), 'wb')
        pickle.dump(state, f)
        f.close()

    def _update_ready_pieces(self, alert_type, alert):
        """
        Servicio encargado de informar que hay una pieza disponible
        """
        if alert_type == 'read_piece_alert' and self.file:
            self.file.update_piece(alert.piece, alert.buffer)

    def _check_meta(self):
        """
        Servicio encargado de comprobar si los metadatos se han descargado
        """
        if self.status.state >= 3 and self.status.state <= 5 and not self.has_meta:

            # Guardamos los metadatos
            self.meta = self._th.get_torrent_info()

            # Obtenemos la lista de archivos del meta
            fs = self.meta.files()
            if isinstance(fs, list):
                files = fs
            else:
                files = [fs.at(i) for i in xrange(fs.num_files())]

            # Guardamos la lista de archivos
            self.files = self._find_files(files)

            # Marcamos el primer archivo como activo
            self.set_file(self.files[0])

            # Damos por iniciada la descarga
            self.start_time = time.time()

            # Guardamos el .torrent en el cahce
            self._cache.file_complete(self._th.get_torrent_info())

            self.has_meta = True

    def priorize_start_file(self):
        '''
        Servicio encargado de priorizar el principio y final de archivo cuando no hay conexion
        '''
        if self.file and not self.file.cursor:
            num_start_pieces = self.buffer_size - self.last_pieces_priorize  # Cantidad de piezas a priorizar al inicio
            num_end_pieces = self.last_pieces_priorize  # Canridad de piezas a priorizar al final

            pieces_count = 0
            # Priorizamos las ultimas piezas
            for y in range(self.file.last_piece - num_end_pieces, self.file.last_piece + 1):
                if not self._th.have_piece(y):
                    self.prioritize_piece(y, pieces_count)
                    pieces_count += 1

            # Priorizamos las primeras piezas
            for y in range(self.file.first_piece, self.file.last_piece + 1):
                if not self._th.have_piece(y):
                    if pieces_count == self.buffer_size:
                        break
                    self.prioritize_piece(y, pieces_count)
                    pieces_count += 1

    def print_status(self):
        '''
        Servicio encargado de mostrar en el log el estado de la descarga
        '''
        s = self.status
        if self.file:
            archivo = self.file.index
        else:
            archivo = "N/D"
        logger.info(
            '%.2f%% de %.1fMB %s | %.1f kB/s | #%s %d%% | AutoClose: %s | S: %d(%d) P: %d(%d)) | TRK: %d DHT: %d PEX: %d LSD %d | DHT:%s (%d) | Trakers: %d' % \
            (s.progress_file, s.file_size, s.str_state, s._download_rate, archivo, s.buffer, s.timeout, s.num_seeds, \
             s.num_complete, s.num_peers, s.num_incomplete, s.trk_peers, s.dht_peers, s.pex_peers, s.lsd_peers,
             s.dht_state, s.dht_nodes, s.trackers))
