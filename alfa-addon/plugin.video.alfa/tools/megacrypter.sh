#!/bin/bash

VERSION="0.8"

MEGA_API_URL="https://g.api.mega.co.nz"
MEGA_API_KEY=""
MC_API_URL="http://megacrypter.com/api"
OPENSSL_AES_CTR_DEC="openssl enc -d -aes-128-ctr"
OPENSSL_AES_CBC_DEC="openssl enc -a -A -d -aes-128-cbc"
WATCH_DIR="."
WATCHDOG_SLEEP_SECS=5
DOWNLOAD_STOP_FILE="force_stop.tmp"
DOWNLOAD_FINISHED_FILE="download_finished.tmp"

# 1:download url
function watchdog {
	
	echo -e "Watchdog loaded!\n"	
	
	WATCHDOG=true
	
	while [ $WATCHDOG ] && [ "$res" != "$DOWNLOAD_STOP_FILE" ]; do
		sleep $WATCHDOG_SLEEP_SECS
		res=$(ls "$DOWNLOAD_STOP_FILE" 2>&1)
	done
	
	if [ $WATCHDOG ] 
		then
			WATCHDOG=false
			pid=$(pgrep -f "$1")
			kill -s 9 "$pid"
		else
			rm "${WATCH_DIR}/${DOWNLOAD_FINISHED_FILE}"
	fi
	
	echo -e "Watchdog bye bye!\n"
}

# 1:json_string 2:index
function json_param {
	echo -ne "$1" | tr -d '\n' | perl -pe "s/^.*\"$2\" *?\: *?([0-9]+|true|false|\".*?(?<!\\\\)\").*?$/\1/s" | perl -pe "s/^\"(.+)\"$/\1/" | tr -d '\\'
}

# 1:b64_encoded_String
function b64_pad {
	
	b64=$(echo -ne "$1" | tr '\-_' '+/')
	
	pad=$(((4-${#1}%4)%4))
	
	for i in $(seq 1 $pad)
	do
		b64="${b64}="
	done
	
	echo -n "$b64"
}

# 1:string
function md5 {

	echo -n "$1" | md5sum | tr -d -c [:alnum:]
}

# 1:pass 2:double_md5 3:salt
function is_valid_pass {

	if [ $(md5 "$3$(md5 "$1")$3") != $2 ]
	then
		echo -n "0"
	else
		echo -n "1"
	fi
}

# 1:hex_raw_key
function hrk2hk {
	key[0]=$(( 0x${1:0:16} ^ 0x${1:32:16} ))

	key[1]=$(( 0x${1:16:16} ^ 0x${1:48:16} ))

	printf "%016x" ${key[*]}
} 

echo -e "\nThis is MEGA-DOWN $VERSION"

if [ -z $1 ]
then
	echo -e "\n$0 <mega_url|mc_url> [output_file] [mc_url_pass]\n\nNote: use '-' for output to STDOUT\n"
else
	
	if [ $(echo -n $1 | grep -E -o 'mega\.co\.nz') ]
	then
		
		#MEGA.CO.NZ LINK
		
		file_id=$(echo -n $1 | perl -pe "s/^.*\/#!(.+)!.*$/\1/s")
		
		file_key=$(echo -n $1 | perl -pe "s/^.*\/#!.+!(.*)$/\1/s")
		
		hex_raw_key=$(echo -n $(b64_pad $file_key) | base64 -d -i 2>/dev/null | od -An -t x1 | tr -d '\n ')
		
		mega_req_url="${MEGA_API_URL}/cs?id=$seqno&ak=$MEGA_API_KEY"
		
		mega_req_json="[{\"a\":\"g\", \"p\":\"$file_id\"}]"
		
		mega_res_json=$(curl -s -X POST --data-binary "$mega_req_json" "$mega_req_url")
		
		if [ $(echo -n "$mega_res_json" | grep -E -o '\[\-[0-9]\]') ]
		then
			error_code=$(echo -n "$mega_res_json" | perl -pe "s/^.*\[(.*?)\].*$/\1/s")
			echo -e "\nMEGA ERROR: $error_code\n" 1>&2
			exit
		else	
			file_size=$(json_param "$mega_res_json" s)
			
			at=$(json_param "$mega_res_json" at)

			hex_key=$(hrk2hk "$hex_raw_key")
			
			at_dec_json=$(echo -n $(b64_pad "$at") | $OPENSSL_AES_CBC_DEC -K $hex_key -iv "00000000000000000000000000000000" -nopad)
			
			if [ $(echo -n "$at_dec_json" | grep -E -o 'MEGA') ]
			then
				file_name=$(json_param "$(echo -n $(b64_pad "$at") | $OPENSSL_AES_CBC_DEC -K $hex_key -iv "00000000000000000000000000000000" -nopad)" n)
				
				mega_req_json="[{\"a\":\"g\", \"g\":\"1\", \"p\":\"$file_id\"}]"
				
				mega_res_json=$(curl -s -X POST --data-binary "$mega_req_json" "$mega_req_url")
				
				dl_temp_url=$(json_param "$mega_res_json" g)
			else
				echo -e "\nMEGA ERROR: bad link\n" 1>&2
				exit
			fi
		fi
	else
		
		#MEGACRYPTER LINK
		
		info_link=$(curl -s -X POST --data-binary "{\"m\":\"info\", \"link\":\"$1\"}" "$MC_API_URL")

		if [ $(echo $info_link | grep '"error"') ]
		then
			error_code=$(json_param "$info_link" error)
			echo -e "\nMEGACRYPTER ERROR: $error_code\n" 1>&2
		else
			if [ -z $2 ]
			then
				file_name=$(json_param "$info_link" name)
			else
				file_name="$2"
			fi		
			
			pass=$(json_param "$info_link" pass)
			
			if [ $pass != "false" ]
			then
				arr_pass=(${pass//#/ })
				pass_double_md5=${arr_pass[0]}
				pass_salt=${arr_pass[1]}
				pass=""

				if [ $3 ]
				then
					pass="$3"
								
					if [ $(is_valid_pass $pass $pass_double_md5 $pass_salt) -eq 0 ]
					then
						pass=""
					fi
				fi
				
				if [ -z $pass ]
				then		
					read -e -p "Link is password protected. Enter password: " pass
							
					until [ $(is_valid_pass $pass $pass_double_md5 $pass_salt) -eq 1 ]; do
						read -e -p "Wrong password! Try again: " pass
					done		
				fi

				hex_raw_key=$(echo -n $(b64_pad $(json_param "$info_link" key)) | $OPENSSL_AES_CBC_DEC -K $(md5 "$pass") -iv "00000000000000000000000000000000" | od -An -t x1 | tr -d '\n ')
				
				if [ -z $2 ]
				then
					file_name=$(echo -n $(b64_pad "$file_name") | $OPENSSL_AES_CBC_DEC -K $(md5 "$pass") -iv "00000000000000000000000000000000")
				fi
			else
				hex_raw_key=$(echo -n $(b64_pad $(json_param "$info_link" key)) | base64 -d -i 2>/dev/null | od -An -t x1 | tr -d '\n ')	
			fi

			file_size=$(json_param "$info_link" size)

			hex_key=$(hrk2hk "$hex_raw_key")

			dl_link=$(curl -s -X POST --data-binary "{\"m\":\"dl\", \"link\":\"$1\"}" "$MC_API_URL")

			dl_temp_url=$(json_param "$dl_link" url)
		fi
	fi
	
	watchdog $dl_temp_url &

	echo -e "Downloading...!\n"
	
	if [ "$2" != "-" ]
		then
			hex_iv="${hex_raw_key:32:16}0000000000000000"				
			curl -s $dl_temp_url | $OPENSSL_AES_CTR_DEC -K $hex_key -iv $hex_iv > "${file_name}"
		else
			hex_iv="${hex_raw_key:32:16}0000000000000000"
			curl -s $dl_temp_url | $OPENSSL_AES_CTR_DEC -K $hex_key -iv $hex_iv
		fi
	
	if [ $WATCHDOG ] 
		then
				WATCHDOG=false
				echo -e "\nFILE DOWNLOADED :)!\n"
				touch "${WATCH_DIR}/${DOWNLOAD_FINISHED_FILE}"
		else
				echo -e "\nFILE DOWNLOAD STOPPED!\n"
				rm "${WATCH_DIR}/${DOWNLOAD_STOP_FILE}"
		fi

fi
