PYTHON38 ?= pyinterp/venv/bin/python

all: bundle

include/lang/py/pyinterp.js: ./pyinterp/pyinterp/pyinterp/__init__.py
	@echo "*** Building include/lang/py/pyinterp.js:"
	@echo "***   Running make on pyinterp"
	cd ./pyinterp && $(MAKE) clean-venv  # Delete the venv, may have absolute references to copied folder
	cd ./pyinterp/etc/zp && $(MAKE) pyinterp-venv && $(MAKE) pyinterp
	@echo "***   Backing up old include/lang/py/pyinterp.js"
	cp ./include/lang/py/pyinterp.js ./include/lang/py/pyinterp.js.bk 2>/dev/null || :
	@echo "***   Creating include/lang/py/pyinterp.js"
	cp ./pyinterp/etc/zp/_tmpdir/pyinterp.js ./include/lang/py/pyinterp.js
	js-beautify -r -s 2 ./include/lang/py/pyinterp.js

include/lang/py/style.js:
	@echo "*** Building include/lang/py/style.js:"
	@echo "***   Running make on style"
	cd ./pyinterp/etc/zp && $(MAKE) style
	@echo "***   Backing up old include/lang/py/style.js"
	cp ./include/lang/py/style.js ./include/lang/py/style.js.bk 2>/dev/null || :
	@echo "***   Creating include/lang/py/style.js"
	cp ./pyinterp/etc/zp/_tmpdir/style.js ./include/lang/py/style.js

.PHONY: serve
serve: bundle
	$(PYTHON38) -m http.server 8999 --bind 127.0.0.1

codeboot.bundle.min.js: codeboot.bundle.js
	uglifyjs codeboot.bundle.js --compress > codeboot.bundle.min.js

bundle-min: codeboot.bundle.css codeboot.bundle.min.js
	inliner index.html | sed -e '1h;2,$$H;$$!d;g' -re 's/~~s\ns~~/ nl /g' > codeboot_bundle.html

bundle: codeboot.bundle.css codeboot.bundle.js
	# requires inliner (from npm) installed
	# The 'sed' call solves a weird bug from inliner (https://github.com/remy/inliner/issues/221)
	# We probably should move away from inliner eventually...
	inliner index.html | sed -e '1h;2,$$H;$$!d;g' -re 's/~~s\ns~~/ nl /g' > codeboot_bundle.html

codeboot.bundle.css: \
include/bootstrap-4.5.0-dist/css/bootstrap.min.css \
include/codemirror-5.56.0/lib/codemirror.css \
include/codemirror-5.56.0/addon/dialog/dialog.css \
include/jspreadsheet-4.9.11/dist/jspreadsheet.css \
include/jsuites-4.9.34/dist/jsuites.css \
include/codeboot.css \

	@echo "*** Building codeboot.bundle.css"
	@rm -f $@
	@touch $@
	@for f in $+; do \
	  cat $$f >> $@; \
	  echo >> $@; \
	done

codeboot.bundle.js: \
include/jquery-3.2.1.min.js \
include/jquery.clippy.min.js \
include/bootstrap-4.5.0-dist/js/bootstrap.bundle.min.js \
include/popper.min.js \
include/tippy-bundle.umd.min.js \
include/codemirror-5.56.0/lib/codemirror.js \
include/codemirror-5.56.0/addon/edit/matchbrackets.js \
include/codemirror-5.56.0/addon/display/rulers.js \
include/codemirror-5.56.0/addon/search/searchcursor.js \
include/codemirror-5.56.0/addon/search/search.js \
include/codemirror-5.56.0/addon/comment/comment.js \
include/codemirror-5.56.0/addon/dialog/dialog.js \
include/codemirror-5.56.0/keymap/emacs.js \
include/codemirror-5.56.0/mode/javascript/javascript.js \
include/codemirror-5.56.0/mode/python/python.js \
include/jspreadsheet-4.9.11/dist/jspreadsheet.js \
include/jsuites-4.9.34/dist/jsuites.js \
include/jsrsasign-8.0.20/jsrsasign-all-min.js \
include/lzma-js-2.3.2/lzma_worker-min.js \
include/download.js \
include/lang.js \
include/lang/js/num.js \
include/int.js \
include/float.js \
include/lang/js/js.js \
include/lang/js/system.js \
include/lang/js/scanner.js \
include/lang/js/parser.js \
include/lang/js/pp.js \
include/lang/js/ast-passes.js \
include/lang/js/eval.js \
include/lang/js/builtins.js \
include/lang/py/py.js \
include/lang/py/pyinterp.js \
include/lang/py/style.js \
include/codeboot.js \
include/config.js \
include/sign.js \
include/i18n.js \
include/drawing.js \
include/actions.js \
include/editors.js \
include/fs.js \
include/storage.js \
include/tutorial.js \
include/jquery.visibility.js \
include/vega.min.js \
include/vega-lite.min.js \
include/vega-lite-api.min.js \
include/vega-tooltip.min.js \
include/charts.js \

	@echo "*** Building codeboot.bundle.js"
	@rm -f $@
	@touch $@
	@for f in $+; do \
	  cat $$f >> $@; \
	  echo >> $@; \
	done


clean:
	rm -rf codeboot.bundle.js codeboot.bundle.css
