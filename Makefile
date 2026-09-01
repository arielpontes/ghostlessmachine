LAN_IP := $(shell ipconfig getifaddr en0 || ipconfig getifaddr en1)
LAN_URL := http://$(LAN_IP):1313/ghostlessmachine/

.PHONY: start
start:
	hugo server --bind 0.0.0.0 --baseURL $(LAN_URL)
