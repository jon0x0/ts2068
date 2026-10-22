PYTHON ?= python3
NODE ?= node
SJASMPLUS ?= sjasmplus
ROM ?=
FONT_ARGS = $(if $(ROM),--rom "$(ROM)",)
TSRUN ?= ../../TSRun
FUSE ?= fuse
.PHONY: all test test-tsrun test-fuse test-directory package
all:
	$(PYTHON) tools/build.py --assembler "$(SJASMPLUS)" $(FONT_ARGS)
test: all
	$(PYTHON) -m unittest discover -s tests -v
test-tsrun: test
	$(NODE) tools/test_tsrun.mjs "$(TSRUN)"
	$(NODE) tools/test_storage.mjs "$(TSRUN)"
test-fuse: test
	$(PYTHON) tools/test_fuse.py --fuse "$(FUSE)"
	$(PYTHON) tools/test_fuse.py --fuse "$(FUSE)" --command "SUBMIT DEMO" --expect "Assembled on the TS2068!"
test-directory: test
	$(NODE) tools/test_directory.mjs "$(TSRUN)"
	$(NODE) tools/test_directory.mjs "$(TSRUN)" --large --boot-only
package: all
	$(PYTHON) tools/package.py

.PHONY: oliger test-oliger package-oliger
oliger:
	$(PYTHON) tools/build.py --profile oliger --assembler "$(SJASMPLUS)" $(FONT_ARGS)
test-oliger: oliger
	$(PYTHON) -m unittest discover -s tests -v
	$(NODE) tools/test_oliger_backend.mjs "$(TSRUN)"
	$(PYTHON) tools/test_oliger_fuse.py --fuse "$(FUSE)"
	$(PYTHON) tools/test_oliger_fuse.py --fuse "$(FUSE)" --command "SUBMIT DEMO" --expect "Assembled on the TS2068!" --label submit
package-oliger: oliger
	$(PYTHON) tools/package.py
