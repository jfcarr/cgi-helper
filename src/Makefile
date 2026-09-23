SRC = simple_cgi.py
TGT_DIR = ../www/cgi-bin
TGT = simple_py.cgi

default:
	@echo 'Targets:'
	@echo '  run   -- Run the script directly.'
	@echo '  copy  -- Copy the script to the www test folder.'

run:
	./$(SRC)

copy:
	mkdir -p $(TGT_DIR) && cp $(SRC) $(TGT_DIR)/$(TGT)
	chmod u+x $(TGT_DIR)/$(TGT)
