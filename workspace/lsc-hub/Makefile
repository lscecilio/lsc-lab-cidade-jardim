REMOTE=root@100.77.253.80
APP_DIR=/opt/lsc-lab/apps/lsc-hub
DOC_FILES=../lsc-juridico-os.html lsc-dev-os.html lsc-financeiro-os.html lsc-growth-os.html lsc-cs-os.html lsc-mkt-saas-os.html lsc-data-os.html
PROCESS_FILES=../lsc-juridico-processes.json lsc-dev-processes.json lsc-fin-processes.json lsc-growth-processes.json lsc-cs-processes.json lsc-mkt-saas-processes.json lsc-data-processes.json

deploy:
	ssh $(REMOTE) "mkdir -p $(APP_DIR)/data $(APP_DIR)/docs"
	scp Makefile server.py hub.html requirements.txt $(REMOTE):$(APP_DIR)/
	scp $(DOC_FILES) $(REMOTE):$(APP_DIR)/docs/
	scp $(PROCESS_FILES) $(REMOTE):$(APP_DIR)/data/
	ssh $(REMOTE) "cd $(APP_DIR) && pip3 install -r requirements.txt -q && systemctl restart lsc-hub"

.PHONY: deploy
