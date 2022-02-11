/* ----- UI helpers ----- */

CodeBootVM.prototype.scrollTo = function (elementOrSelector) {
    var elementOffset = $(elementOrSelector).position().top;
    $('.cb-editors').animate({scrollTop: elementOffset}, 400);
};

/* ----- Internal file system ----- */

var BUILTIN_FILES = {

    'sample/hello.js' :
        '// This program prints a famous greeting\n' +
        '\n' +
        'print("Hello, world!");\n',

    'sample/hello.py' :
        '# This program prints a famous greeting\n' +
        '\n' +
        'print("Hello, world!")\n',

    'sample/sqrt2.js' :
        '// This program computes the square root of 2 without using Math.sqrt\n' +
        '\n' +
        'var n = 2;       // number whose square root is to be computed\n' +
        'var approx = n;  // first approximation of sqrt(n)\n' +
        '\n' +
        'for (;;) {\n' +
        '    next = (approx + n/approx) / 2;  // improve approximation\n' +
        '    if (next == approx)              // stop when no improvement\n' +
        '        break;\n' +
        '}\n' +
        '\n' +
        'print(approx);  // print square root of n\n',

    'sample/sqrt2.py' :
        '# This program computes the square root of 2 without using math.sqrt\n' +
        '\n' +
        'n = 2       # number whose square root is to be computed\n' +
        'approx = n  # first approximation of sqrt(n)\n' +
        '\n' +
        'while True:\n' +
        '    next = (approx + n/approx) / 2  # improve approximation\n' +
        '    if next == approx:              # stop when no improvement\n' +
        '        break\n' +
        '    approx = next\n' +
        '\n' +
        'print(approx)  # print square root of n\n'
};

BUILTIN_FILES = {};
NEW_FILE_DEFAULT_CONTENT = '';

function CodeBootFile(fs, filename, content, opts) {

    var file = this;
    var vm = fs.vm;

    file.fs = fs;
    file.filename = filename;
    file.content = (content !== undefined) ? content : NEW_FILE_DEFAULT_CONTENT;
    file.cursor = null;
    file.stamp = 0;
    file.preferredEditorView = null;

    new CodeBootFileEditor(file); // initializes file.fe

    if (opts) {
        for (var prop in opts) {
            file[prop] = opts[prop];
        }
    }
}

CodeBootFile.prototype.extension = function (filename) {

    var file = this;

    var dot = filename.lastIndexOf('.');
    var slash = filename.lastIndexOf('/');

    if (dot > slash)
        return filename.slice(dot);
    else
        return '';
};

CodeBootFile.prototype.getExtension = function () {

    var file = this;

    return file.extension(file.filename);
};

CodeBootFile.prototype.getContent = function () {

    var file = this;

    if (file.fe.isEnabled()) {
        return file.fe.getValue();
    } else {
        return file.content;
    }
};

CodeBootFile.prototype.setContent = function (content) {

    var file = this;

    file.content = content;
    file.fe.setValue(content);
};

CodeBootFile.prototype.save = function () {

    var file = this;

    if (file.fe.isEnabled()) {
        var oldContent = file.content;
        var newContent = file.fe.getValue();
        if (newContent !== oldContent) {
            file.content = newContent;
            file.stamp += 1;
        }
    }
};

CodeBootFile.prototype.serialize = function () {

    var file = this;

    var json = {
        filename: file.filename,
        content: file.getContent(),
        cursor: file.cursor === null ?
                {line: 0, ch: 0} :
                {line: file.cursor.line, ch: file.cursor.ch},
        stamp: file.stamp,
        preferredEditorView: file.preferredEditorView
    };

    return json;
};

CodeBootFile.prototype.clone = function () {

    var file = this;
    var other = new CodeBootFile(file.fs, file.filename, file.content);

    for (var prop in file) {
        if (Object.prototype.hasOwnProperty.call(file, prop)) {
            other[prop] = file[prop];
        }
    }

    return other;
};

CodeBootFile.prototype.setReadOnly = function (readOnly) {

    var file = this;

    file.fe.setReadOnly(readOnly);
};

CodeBootFile.prototype.toURL = function (isolated) {

    var file = this;
    var fs = file.fs;
    var vm = fs.vm;

    var cmds = ['F' + toSafeBase64(file.filename) + ',' +
                toSafeBase64(file.getContent())];

    return vm.commandsToURL(cmds, isolated);
};

function CodeBootFileSystem(vm) {

    var fs = this;

    fs.vm = vm;

    new CodeBootFileEditorManager(fs); // initializes fs.fem

    vm.fs = fs;
}

CodeBootFileSystem.prototype.init = function () {

    var fs = this;

    fs.removeAllFileEditors();
    fs.initFileTabs();
    fs.clear();
    fs.rebuildFileMenu();
};

CodeBootFileSystem.prototype.initFileTabs = function () {

    var fs = this;
    var vm = fs.vm;

    vm.withElem('.cb-file-tabs', function (tabsElem) {
        var sentinelTab = document.createElement('li');
        sentinelTab.className = 'cb-file-tab';
        sentinelTab.innerHTML = '<div class="cb-tab-spacer"></div>';
        tabsElem.innerHTML = '';
        tabsElem.appendChild(sentinelTab);
        fs.setupTabDragAndDrop(sentinelTab, null);
    });
};

CodeBootFileSystem.prototype.setupTabDragAndDrop = function (fileTab, fe) {

    var fs = this;

    var dragoverNest = 0;

    function resetDragoverNest() {
        dragoverNest = 0;
        fileTab.classList.remove('cb-drag-over');
    }

    function handleDragStart(event) {
        var file = fe.file;
        var dt = event.dataTransfer;
        dt.effectAllowed = 'copyMove';
        fileTab.classList.add('cb-dragging');
        fileTab.setAttribute('data-cb-dragstart', '');
        var shareableData = file.getShareableData();
        for (var i=0; i<shareableData.length; i++) {
            dt.setData(shareableData[i][0], shareableData[i][1]);
        }
        dt.setData('text/codeboot-file-name', file.filename);
    }

    function handleDragEnd(event) {
        fileTab.classList.remove('cb-dragging');
    }

    function handleDragEnter(event) {
        if (dragoverNest++ === 0) {
            fileTab.classList.add('cb-drag-over');
        }
    }

    function handleDragLeave(event) {
        if (--dragoverNest === 0) {
            resetDragoverNest();
        }
    }

    function handleDragOver(event) {
        fileTab.removeAttribute('data-cb-dragstart');
        if (event.dataTransfer.getData('text/codeboot-file-name') !== '') {
            return false;
        }
    }

    function handleDrop(event) {
        resetDragoverNest();
        event.stopPropagation(); // stops the browser from redirecting.
        var dt = event.dataTransfer;
        var sourceFilename = event.dataTransfer.getData('text/codeboot-file-name');
        if (sourceFilename === '') {
            var vm = fs.vm;
            if (vm.editable) {
                vm.handleDrop(event);
            }
            event.preventDefault();
        } else {
            var parent = fileTab.parentNode;
            var index = Array.prototype.indexOf.call(parent.childNodes, fileTab);
            var fem = fs.fem;
            fem.moveTabs(fem.indexOfFilename(sourceFilename), index);
        }
        return false;
    }

    if (fe) {
        fileTab.addEventListener('dragstart', handleDragStart);
        fileTab.addEventListener('dragend', handleDragEnd);
    }

    fileTab.addEventListener('dragenter', handleDragEnter);
    fileTab.addEventListener('dragleave', handleDragLeave);
    fileTab.addEventListener('dragover', handleDragOver);
    fileTab.addEventListener('drop', handleDrop);
};

CodeBootFileSystem.prototype.clear = function () {

    var fs = this;

    fs.builtins = {};
    fs.files = Object.create(fs.builtins);
    fs._loadBuiltins();
};

CodeBootFileSystem.prototype._loadBuiltins = function () {

    var fs = this;

    for (var filename in BUILTIN_FILES) {
        var f = new CodeBootFile(fs, filename, BUILTIN_FILES[filename]);
        fs.builtins[filename] = f;
    };
};

CodeBootFileSystem.prototype._asFilename = function (fileOrFilename) {

    var fs = this;

    if (typeof fileOrFilename === 'string') return fileOrFilename;
    return fileOrFilename.filename;
};

CodeBootFileSystem.prototype._asFile = function (fileOrFilename) {

    var fs = this;

    if (typeof fileOrFilename !== 'string') return fileOrFilename;
    return fs.getByName(fileOrFilename);
};

CodeBootFileSystem.prototype.isBuiltin = function (fileOrFilename) {

    var fs = this;
    var filename = fs._asFilename(fileOrFilename);

    return Object.prototype.hasOwnProperty.call(fs.builtins, filename);
};

CodeBootFileSystem.prototype.addFile = function (f) {

    var fs = this;

    fs.files[f.filename] = f;
};

CodeBootFileSystem.prototype.hasFile = function (fileOrFilename) {

    var fs = this;
    var filename = fs._asFilename(fileOrFilename);

    return Object.prototype.hasOwnProperty.call(fs.files, filename) ||
           Object.prototype.hasOwnProperty.call(fs.builtins, filename);
};

CodeBootFileSystem.prototype.generateUniqueFilename = function () {

    var fs = this;
    var prefix = 'untitled';
    var candidateName;

    for (var index = 1; ; index++) {
        candidateName = prefix + (index===1 ? '' : index) + fs.vm.lang.getExts()[0];
        if (!fs.hasFile(candidateName)) break;
    }

    return candidateName;
};

CodeBootFileSystem.prototype.getByName = function (filename) {

    var fs = this;

    if (!fs.hasFile(filename)) {
        throw 'File not found: "' + filename + '"';
    }

    var file = fs.files[filename];

    if (!Object.prototype.hasOwnProperty.call(fs.files, filename)) {
        // This is a builtin file, make an editable copy
        file = file.clone();
        fs.files[filename] = file;
    }

    return file;
};

CodeBootFileSystem.prototype.deleteFile = function (fileOrFilename) {

    var fs = this;
    var filename = fs._asFilename(fileOrFilename);

    if (fs.hasFile(filename)) {
        delete fs.files[filename];
        return true;
    }

    return false;
};

CodeBootFileSystem.prototype.renameFile = function (fileOrFilename, newFilename) {

    var fs = this;

    if (fs.hasFile(newFilename)) {
        throw 'File already exists: "' + newFilename + '"';
    }

    var file = fs._asFile(fileOrFilename);

    delete fs.files[file.filename];
    file.filename = newFilename;
    fs.addFile(file);
};

CodeBootFileSystem.prototype.getContent = function (fileOrFilename) {

    var fs = this;
    var file = fs._asFile(fileOrFilename);

    return file.getContent();
};

CodeBootFileSystem.prototype.getTextEditor = function (fileOrFilename) {

    var fs = this;

    return fs._asFile(fileOrFilename).fe.textEditor;
};

CodeBootFileSystem.prototype.setContent = function (fileOrFilename, content) {

    var fs = this;
    var file = fs._asFile(fileOrFilename);

    file.setContent(content);
};

CodeBootFileSystem.prototype.each = function (callback, selector) {

    var fs = this;

    if (!selector) selector = function (f) { return true; };

    for (var filename in fs.files) {

        if (!fs.hasFile(filename)) continue; // Prune Object method name

        var file = fs.getByName(filename);
        if (selector(file)) {
            callback(file);
        }
    }
};

CodeBootFileSystem.prototype.forEachFileEditor = function (callback) {

    var fs = this;

    fs.fem.fileEditors.forEach(callback);
};

CodeBootFileSystem.prototype.serialize = function () {

    var fs = this;
    var json = [];
    var isUserFile = function (file) {
        return Object.prototype.hasOwnProperty.call(fs.files, file.filename);
    };

    fs.each(function (file) {
        json.push(file.serialize());
    },
    isUserFile);

    return json;
};

CodeBootFileSystem.prototype.restore = function (json) {

    var fs = this;

    fs.clear();

    for (var i = 0; i < json.length; i++) {
        var fileProps = json[i];
        var file = new CodeBootFile(fs, fileProps.filename, fileProps.content, fileProps);
        fs.addFile(file);
    }
};

CodeBootFileSystem.prototype.rebuildFileMenu = function () {

    var fs = this;
    var vm = fs.vm;

    fs.vm.forEachElem('.cb-file-selection', function (elem) {

        elem.innerHTML = ''; // remove children

        var newFile = fs.newMenuItem(elem,
                                     'cb-file-new dropdown-item',
                                     vm.polyglotHTML('New file'));

        elem.appendChild(newFile);

        newFile.addEventListener('click', function (event) {
            fs.newFile();
        });

        var resetFS = fs.newMenuItem(elem,
                                     'cb-reset-filesystem dropdown-item',
                                     vm.polyglotHTML('Reset filesystem'));

        elem.appendChild(resetFS);

        resetFS.addEventListener('click', function (event) {
            vm.confirmHTML(vm.polyglotHTML('Reset filesystem? This cannot be undone.'),
                           function (yes) {
                               if (yes) {
                                   fs.init();
                               }
                           });
        });

        fs.addDividerToMenu(elem);

        fs.each(function (file) {
            fs.addFileToMenu(elem, file);
        });
    });
};

CodeBootFileSystem.prototype.newMenuItem = function (elem, cls, html) {

    var item = document.createElement('a');
    item.className = cls;
    item.href = '#';

    var span = document.createElement('span');
    span.innerHTML = html;

    item.appendChild(span);

    return item;
};

CodeBootFileSystem.prototype.addDividerToMenu = function (elem) {

    var item = document.createElement('div');
    item.className = 'dropdown-divider';

    elem.appendChild(item);

    return item;
};

CodeBootFileSystem.prototype.addButton = function (buttons, title, html, onClick) {

    var button = document.createElement('button');

    button.className = 'close';

    if (title) {
        button.setAttribute('data-toggle', 'tooltip');
        button.setAttribute('data-delay', '750');
        button.setAttribute('data-animation', 'false');
        button.setAttribute('data-placement', 'bottom');
        button.setAttribute('data-title', title);
    }

    button.innerHTML = html;

    button.addEventListener('click', onClick);

    buttons.appendChild(button);

    return button;
};

CodeBootFileSystem.prototype.addFileToMenu = function (elem, file) {

    var fs = this;
    var vm = fs.vm;
    var filename = file.filename;

    function dismissMenu() {
        $(elem).find($('[data-toggle="tooltip"]')).tooltip('hide');
        elem.classList.remove('show');
    }

    var item = fs.newMenuItem(elem,
                              'dropdown-item',
                              CodeBoot.prototype.escapeHTML(filename));

    item.setAttribute('data-cb-filename', filename);

    item.addEventListener('click', function (event) {
        event.stopPropagation();
        dismissMenu();
        file.fe.edit();
    });

    var nodes = elem.childNodes;

    for (var i=2; i<nodes.length; i++) {
        var e = nodes[i];
        if (filename < e.getAttribute('data-cb-filename')) {
            elem.insertBefore(item, e);
            return;
        }
    }

    elem.appendChild(item);

    $(elem).find($('[data-toggle="tooltip"]')).tooltip();
};

CodeBootFile.prototype.delete = function () {

    var file = this;
    var fs = file.fs;
    var vm = fs.vm;
    var filename = file.filename;

    vm.confirmHTML(vm.polyglotHTML('Delete file "{}"? This cannot be undone.',
                                   [filename]),
                   function (yes) {
                       if (yes) {
                           file.fe.disable(); // TODO: do this based on filename decause it is done async and the file may have vanished
                           fs.deleteFile(file);
                           fs.rebuildFileMenu();
                       }
                   });
};

CodeBootFile.prototype.download = function () {

    var file = this;
    var filename = file.filename;
    var content = file.getContent();

    download(content, filename, 'text/plain');
/*deprecated
    var elem = document.createElement('a');
    elem.setAttribute('href', 'data:text/plain;charset=utf-8,' + encodeURIComponent(content));
    elem.setAttribute('download', filename);

    elem.style.display = 'none';
    document.body.appendChild(elem);

    elem.click();

    document.body.removeChild(elem);
*/
};

CodeBootFile.prototype.email = function () {
    var file = this;
    var filename = file.filename;
    var content = file.getContent();
    var url = ''; //editor_URL(content, filename) + '\n\n\n';
    var subject = encodeURIComponent(filename);
    var body = encodeURIComponent(url+content);
    var href = 'mailto:?subject=' + subject + '&body=' + body;
    var w = window.open(href, '_blank');
    if (w) w.close();
};

CodeBootVM.prototype.copyTextToClipboard = function (text) {

    var vm = this;

    var textArea = document.createElement('textarea');
    textArea.value = text;
    document.body.appendChild(textArea);
    textArea.select();
    document.execCommand('copy');
    document.body.removeChild(textArea);
};

/*
CodeBootFile.prototype.copyToClipboardOld = function () {

    var file = this;
    var filename = file.filename;
    var shareableData = file.getShareableData();

    function handler(event) {
        for (var i=0; i<shareableData.length; i++) {
            event.clipboardData.setData(shareableData[i][0], shareableData[i][1]);
        }
        event.preventDefault();
    }

    document.addEventListener('copy', handler);
    document.execCommand('copy');
    document.removeEventListener('copy', handler);
};
*/

CodeBootFile.prototype.copyToClipboard = function () {

    var file = this;
    var shareableData = file.getShareableData();

    var data = {};

    for (var i=0; i<shareableData.length; i++) {
        data[shareableData[i][0]] = shareableData[i][1];
    }

    try {
        navigator.clipboard.write([
            new ClipboardItem(data)
        ]);
    } catch (err) {
        console.error(err.name, err.message);
    }
};

CodeBootFile.prototype.toHTMLText = function (fontSize, fontFamily) {

    var file = this;
    var fe = file.fe;
    var textEditor = fe.textEditor;

    if (fontSize === void 0) {
        fontSize = '18px';
    }

    if (fontFamily === void 0) {
        fontFamily = '\'Hack\', \'Lucida Console\', Monaco, monospace'
    }

    if (textEditor === null) {
        return null;
    } else {

        var styles = ['text-transform', 'color', 'font-weight'];
        var HTMLText;

        if (fontSize !== '' || fontFamily !== '') {
            HTMLText = '<pre style="';
            if (fontSize !== '') {
                HTMLText += 'font-size:' + fontSize + ';';
            }
            if (fontFamily !== '') {
                HTMLText += 'font-family:' + fontFamily + ';';
            }
            HTMLText += '">';
        } else {
            HTMLText = '<pre>';
        }

        var nbLines = textEditor.cm.lineCount();

        for (var i=0; i<nbLines; i++) {
            HTMLText += '\n';
            var lineTokens = textEditor.cm.getLineTokens(i, true);
            for (var j=0; j<lineTokens.length; j++) {
                var t = lineTokens[j];
                var token = CodeBoot.prototype.escapeHTML(t.string);
                var tokenType = t.type;
                if (tokenType) {

                    var elem = document.querySelectorAll('.cm-'+tokenType);
                    var css = '';
                    var compStyle = window.getComputedStyle(elem[0], null);

                    styles.forEach(function (style) {
                        css += style + ':' + compStyle.getPropertyValue(style) + ';';
                    });

                    HTMLText += '<span style="' + css + '">';
                } else {
                    HTMLText += '<span>';
                }
                HTMLText += token + '</span>';
            }
        }
        HTMLText += '</pre>';

        return HTMLText;
    }
};

CodeBootFile.prototype.getShareableData = function (fontSize, fontFamily) {

    var file = this;
    var fe = file.fe;
    var filename = file.filename;
    var content = file.getContent();
    var result = [];
    var ext = file.extension(filename);

    var url = file.toURL(false);

    if (fontSize === void 0) {
        fontSize = '18px';
    }

    if (ext === '.csv' || ext === '.tsv') {
        result.push(['text/csv', content]);
    } else {
        var HTMLText = file.toHTMLText(fontSize, fontFamily);
        if (HTMLText !== null) {
            if (url !== null) {
                var link = '<a href="' + url + '"';
                if (fontSize !== '') {
                    link += ' style="font-size:' + fontSize + ';"';
                }
                link += '>' + CodeBoot.prototype.escapeHTML(filename) + '</a>';
                HTMLText = link + '<br><br>\n' + HTMLText;
            }
            result.push(['text/html', HTMLText]);
        }
    }

    content = (url !== null ? url + '\n' : '') + filename + '\n\n' + content;

    result.push(['text/plain', content]);

    if (url !== null) {
        result.push(['text/uri-list', url]);
    }

    return result;
};

CodeBootFileSystem.prototype.openFile = function (fileOrFilename) {

    var fs = this;
    var file = fs._asFile(fileOrFilename);

    file.fe.edit();
};

CodeBootFileSystem.prototype.createFile = function (filename, content, opts) {

    var fs = this;

    if (filename === undefined) {
        filename = fs.generateUniqueFilename();
    }

    var file = new CodeBootFile(fs, filename, content, opts);

    fs.addFile(file);
    fs.rebuildFileMenu();

    return file;
};

CodeBootFileSystem.prototype.newFile = function (filename, content, opts) {

    var fs = this;

    var file = fs.createFile(filename, content, opts);

    file.fe.edit();

    return file;
};

CodeBootFileSystem.prototype.openFileExistingOrNew = function (filename) {

    var fs = this;

    if (fs.hasFile(filename)) {
        fs.openFile(filename);
        return true;
    } else {
        fs.newFile(filename);
        return false;
    }
};

CodeBootFileSystem.prototype.removeAllFileEditors = function () {
    var fs = this;
    fs.fem.removeAllFileEditors();
};

//-----------------------------------------------------------------------------

function CodeBootFileEditorManager(fs) {

    var fem = this;

    fs.fem = fem;
    fem.fs = fs;
    fem.fileEditors = [];
    fem.activated = -1;
}

CodeBootFileEditorManager.prototype.currentlyActivated = function () {

    var fem = this;

    return fem.activated >= 0 ? fem.fileEditors[fem.activated] : null;

};

CodeBootFileEditorManager.prototype.isActivated = function (fe) {

    var fem = this;

    return fem.currentlyActivated() === fe;

};

CodeBootFileEditorManager.prototype.indexOf = function (fe) {

    var fem = this;

    for (var i=fem.fileEditors.length-1; i>=0; i--) {
        if (fem.fileEditors[i] === fe) {
            return i;
        }
    }
    return -1;
};

CodeBootFileEditorManager.prototype.indexOfFilename = function (filename) {

    var fem = this;
    var fs = fem.fs;

    if (fs.hasFile(filename)) {
        var file = fs.getByName(filename);
        if (file.fe.isEnabled()) {
            return fem.indexOf(file.fe);
        }
    }

    return -1;
};

CodeBootFileEditorManager.prototype.activate = function (fe) {

    var fem = this;

    if (fe.isActivated()) return; // already activated

    fem.fs.vm.ui.execPointBubble.destroy();

    var i = fem.indexOf(fe);

    if (i < 0) return; // not a valid file editor

    if (fem.activated >= 0) {
        // deactivate currently activated editor
        fem.fileEditors[fem.activated].deactivatePresentation();
    }

    fe.activatePresentation(); // activate file editor

    fem.activated = i; // remember it is activated

    fe.focus();
};

CodeBootFileEditorManager.prototype.add = function (fe) {

    var fem = this;

    fem.fileEditors.push(fe);

    if (fem.activated < 0) {
        fem.show(); // show file editors
        fe.activate(); // activate editor
    }
};

CodeBootFileEditorManager.prototype.setReadOnlyAllFileEditors = function (readOnly) {

    var fem = this;

    for (var i=0; i<fem.fileEditors.length; i++) {
        fem.fileEditors[i].setReadOnly(readOnly);
    }
};

CodeBootFileEditorManager.prototype.removeAllFileEditors = function () {

    var fem = this;

    while (fem.fileEditors.length > 0) {
        fem.remove(fem.fileEditors[fem.fileEditors.length-1]);
    }
};

CodeBootFileEditorManager.prototype.remove = function (fe) {

    var fem = this;
    var i = fem.indexOf(fe);

    if (i < 0) return; // not a valid file editor

    fe.file.save();

    fe.removePresentation();

    fe.fileTab = null;
    fe.fileTabButton = null;
    fe.fileTabInput = null;
    fe.fileTabSpan = null;
    fe.fileContainer = null;
    fe.textEditor = null;
    fe.spreadsheetEditor = null;
    fe.currentEditorView = null;

    fem.fileEditors.splice(i, 1); // remove from file editors

    if (i === fem.activated) {
        fem.activated = -1;
        // need to activate some other file editor
        if (i < fem.fileEditors.length) {
            fem.fileEditors[i].activate();
        } else if (i > 0) {
            fem.fileEditors[i-1].activate();
        } else {
            // no other file editor to activate
            fem.hide();
            fem.fs.vm.replFocus();
        }
    } else if (i < fem.activated) {
        fem.activated--;
    }
};

CodeBootFileEditorManager.prototype.show = function () {

    var fem = this;

//    fem.fs.vm.withElem('.cb-editors', function (elem) {
//        elem.style.display = 'flex';
//    });
};

CodeBootFileEditorManager.prototype.hide = function () {

    var fem = this;

//    fem.fs.vm.withElem('.cb-editors', function (elem) {
//        elem.style.display = 'none';
//    });
};

CodeBootFileEditorManager.prototype.moveTabs = function (sourceIndex, destIndex) {

    var fem = this;
    var fs = fem.fs;

    if (sourceIndex >= 0 && destIndex >= 0) {
        if (sourceIndex < destIndex) destIndex--;
        if (sourceIndex !== destIndex) {

        var vm = fem.fs.vm;

        vm.withElem('.cb-file-tabs', function (tabsElem) {
            vm.withElem('.cb-editors', function (editorsElem) {
                var tabs = tabsElem.childNodes;
                var editors = editorsElem.childNodes;
                var sourceTab = tabs[sourceIndex];
                var sourceEditor = editors[sourceIndex+1];
                tabsElem.removeChild(sourceTab);
                editorsElem.removeChild(sourceEditor);
                var len = fem.fileEditors.length;
                var fe = fem.fileEditors[sourceIndex];
                fem.fileEditors.splice(sourceIndex, 1);
                if (destIndex >= len-1) {
//                    tabsElem.appendChild(sourceTab);
                    var nextTab = tabs[destIndex];
                    tabsElem.insertBefore(sourceTab, nextTab);
                    editorsElem.appendChild(sourceEditor);
                    fem.fileEditors.push(fe);
                } else {
                    var nextTab = tabs[destIndex];
                    var nextEditor = editors[destIndex+1];
                    tabsElem.insertBefore(sourceTab, nextTab);
                    editorsElem.insertBefore(sourceEditor, nextEditor);
                    fem.fileEditors.splice(destIndex, 0, fe);
                }
                // adjust index of activated editor
                if (fem.activated !== -1) {
                    if (fem.activated === sourceIndex) {
                        fem.activated = destIndex;
                    } else if (sourceIndex < destIndex) {
                        if (fem.activated > sourceIndex &&
                            fem.activated <= destIndex) {
                            fem.activated--;
                        }
                    } else {
                        if (fem.activated >= destIndex &&
                            fem.activated < sourceIndex) {
                            fem.activated++;
                        }
                    }
                }
//                fe.activate();
            });
        });
        }
    }
};

//-----------------------------------------------------------------------------

function CodeBootFileEditor(file) {

    var fe = this;

    fe.file = file;
    fe.fileTab = null;
    fe.fileTabButton = null;
    fe.fileTabInput = null;
    fe.fileTabSpan = null;
    fe.fileContainer = null;
    fe.textEditor = null;
    fe.spreadsheetEditor = null;
    fe.currentEditorView = null;

    file.fe = fe;
}

CodeBootFileEditor.prototype.isActivated = function () {

    var fe = this;
    var fs = fe.file.fs;

    return fs.fem.isActivated(fe);
};

CodeBootFileEditor.prototype.activate = function () {

    var fe = this;
    var fs = fe.file.fs;

    fs.fem.activate(fe);
};

CodeBootFileEditor.prototype.activatePresentation = function () {

    var fe = this;

    fe.fileTab.classList.add('active');
    fe.fileContainer.classList.add('active');
//    fe.fileContainer.style.display = 'inline';
    fe.refresh();
};

CodeBootFileEditor.prototype.deactivatePresentation = function () {

    var fe = this;

    fe.fileTab.classList.remove('active');
    fe.fileContainer.classList.remove('active');
//    fe.fileContainer.style.display = 'none';
};

CodeBootFileEditor.prototype.removePresentation = function () {

    var fe = this;
    var vm = fe.file.fs.vm;

    // remove file tab and file container

    vm.withElem('.cb-file-tabs', function (tabsElem) {
        vm.withElem('.cb-editors', function (editorsElem) {
            tabsElem.removeChild(fe.fileTab);
            editorsElem.removeChild(fe.fileContainer);
        });
    });
};

CodeBootFileEditor.prototype.isEnabled = function () {

    var fe = this;

    console.log('CodeBootFileEditor.prototype.isEnabled');
    console.log(fe.textEditor !== null);

    return fe.textEditor !== null;
};

CodeBootFileEditor.prototype.getValue = function () {

    var fe = this;

    val = fe.file.content;

    if (fe.isEnabled()) {
        if (fe.currentEditorView === 'text') {
            val = fe.textEditor.getValue();
        } else if (fe.currentEditorView === 'spreadsheet') {
            val = fe.spreadsheetEditor.getValue();
        }
    }

    console.log('CodeBootFileEditor.prototype.getValue');
    console.log(val);

    return val;
};

CodeBootFileEditor.prototype.setValue = function (val) {

    var fe = this;

    console.log('CodeBootFileEditor.prototype.setValue');
    console.log(val);

    if (fe.isEnabled()) {
        if (fe.currentEditorView === 'text') {
            fe.textEditor.setValue(val);
        } else if (fe.currentEditorView === 'spreadsheet') {
            fe.spreadsheetEditor.setValue(val);
        }
    }
};

CodeBootFileEditor.prototype.edit = function () {

    var fe = this;

    fe.enable();
    fe.activate();
};

CodeBootFileEditor.prototype.focus = function () {

    var fe = this;

    fe.textEditor.focus();
    fe.file.fs.vm.trackTextEditorFocus(fe.textEditor, true);
};

CodeBootFileEditor.prototype.menuHTML = function () {

    var fe = this;
    var vm = fe.file.fs.vm;

    return '\
  <div class="cb-tab-spacer"></div>\
  <div class="cb-tab" data-toggle="dropdown" draggable="true"><input autocomplete="off" autocorrect="off" autocapitalize="off" spellcheck="false"></input><span></span></div>\
  <div class="dropdown-menu">\
\
    <a href="#" class="dropdown-item" data-cb-file-tab-close>' + vm.SVG['close'] + '&nbsp;&nbsp;' + vm.polyglotHTML('Close tab') + '</a>\
    <a href="#" class="dropdown-item" data-cb-file-tab-rename>' + vm.SVG['rename'] + '&nbsp;&nbsp;' + vm.polyglotHTML('Rename file') + '</a>\
    <a href="#" class="dropdown-item" data-cb-file-tab-download>' + vm.SVG['download'] + '&nbsp;&nbsp;' + vm.polyglotHTML('Download file') + '</a>\
    <a href="#" class="dropdown-item" data-cb-file-tab-mail>' + vm.SVG['mail'] + '&nbsp;&nbsp;' + vm.polyglotHTML('Share by email') + '</a>\
    <a href="#" class="dropdown-item" data-cb-file-tab-clipboard>' + vm.SVG['clipboard'] + '&nbsp;&nbsp;' + vm.polyglotHTML('Copy to clipboard') + '</a>\
\
      <div class="dropdown-divider"></div>\
\
      <a href="#" class="dropdown-item" data-cb-file-tab-delete>' + vm.SVG['trash'] + '&nbsp;&nbsp;' + vm.polyglotHTML('Delete file') + '</a>\
\
    <div class="cb-file-tab-editor-view">\
\
      <div class="dropdown-divider"></div>\
\
      <h5 class="dropdown-header">' + vm.polyglotHTML('Editor') + '</h5>\
      <a href="#" class="dropdown-item" data-cb-file-tab-editor-view="text">' + vm.SVG['checkmark'] + '&nbsp;&nbsp;' + vm.polyglotHTML('Text') + '</a>\
      <a href="#" class="dropdown-item" data-cb-file-tab-editor-view="spreadsheet">' + vm.SVG['checkmark'] + '&nbsp;&nbsp;' + vm.polyglotHTML('Spreadsheet') + '</a>\
\
    </div>\
  </div>\
';
};

CodeBootFileEditor.prototype.setFilename = function (filename) {

    var fe = this;

    console.log('CodeBootFileEditor.prototype.setFilename');
    console.log(filename);

    fe.fileTabSpan.innerText = filename;

    var ext = fe.file.extension(filename);

    fe.fileTab.setAttribute('data-cb-file-tab-filename', filename);
    fe.fileTab.setAttribute('data-cb-file-tab-extension', ext);

    var view = (ext === '.csv' || ext === '.tsv') ? 'spreadsheet' : 'text';

    if (fe.file.preferredEditorView === null || view === 'text') {
        fe.setEditorView(view);
    }
};

CodeBootFileEditor.prototype.enable = function () {

    var fe = this;

    if (fe.isEnabled()) return; // noop if currently enabled

    var file = fe.file;
    var filename = file.filename;
    var fs = file.fs;
    var vm = fs.vm;

    // create file tab

    var fileTab = document.createElement('li');
    fileTab.className = 'cb-file-tab dropdown';

    fileTab.innerHTML = fe.menuHTML();

    var fileTabButton = fileTab.querySelector(':scope > .cb-tab');
    var fileTabInput = fileTabButton.querySelector(':scope > input');
    var fileTabSpan  = fileTabButton.querySelector(':scope > span');

    fs.setupTabDragAndDrop(fileTab, fe);

    fileTab.querySelectorAll('.dropdown-item').forEach(function (elem) {
        elem.addEventListener('click', function (event) {

            var elem = event.currentTarget;
            var val;

            if (elem.hasAttribute('data-cb-file-tab-close')) {
                fe.disable();
            } else if (elem.hasAttribute('data-cb-file-tab-rename')) {
                fe.rename();
            } else if (elem.hasAttribute('data-cb-file-tab-download')) {
                fe.file.download();
            } else if (elem.hasAttribute('data-cb-file-tab-mail')) {
                fe.file.email();
            } else if (elem.hasAttribute('data-cb-file-tab-clipboard')) {
                fe.file.copyToClipboard();
            } else if (elem.hasAttribute('data-cb-file-tab-delete')) {
                fe.file.delete();
            } else if (val = elem.getAttribute('data-cb-file-tab-editor-view')) {
                fe.setEditorView(val);
            }

            return true;
        });
    });

    // create file container

    var fileContainer = document.createElement('div');
    fileContainer.className = 'cb-file-container';

    var textarea = document.createElement('textarea');
    textarea.className = 'cb-file-text-editor';

    fileContainer.appendChild(textarea);

    var spreadsheet = document.createElement('div');
    spreadsheet.className = 'cb-file-spreadsheet-editor';

    fileContainer.appendChild(spreadsheet);

    // add file tab and file container

    vm.withElem('.cb-file-tabs', function (tabsElem) {
        vm.withElem('.cb-editors', function (editorsElem) {
            tabsElem.insertBefore(fileTab, tabsElem.lastChild);
            editorsElem.appendChild(fileContainer);
        });
    });

    // create text editor

    var textEditor = new CodeBootTextEditor(textarea, file);

    fileTabButton.addEventListener('click', function (event) {
        if (fileTab.hasAttribute('data-cb-editing')) {
            // show dropdown menu so that the click will end up hiding it
            $(fileTabButton).dropdown('show');
        } else if (!fe.isActivated()) {
            // show dropdown menu so that the click will end up hiding it
            $(fileTabButton).dropdown('show');
            fe.activate();
        }
    });

    fileContainer.addEventListener('click', function (event) {
        textEditor.focus();
    });

    // create spreadsheet editor

    var spreadsheetEditor = new CodeBootSpreadsheetEditor(spreadsheet, fe);

    // remember each element for quick access

    fe.fileTab = fileTab;
    fe.fileTabButton = fileTabButton;
    fe.fileTabInput = fileTabInput;
    fe.fileTabSpan = fileTabSpan;
    fe.fileContainer = fileContainer;
    fe.textEditor = textEditor;
    fe.spreadsheetEditor = spreadsheetEditor;
    fe.currentEditorView = null;

    file.fs.fem.add(fe);

    fe.setEditorView(file.preferredEditorView);
    fe.setFilename(filename);
};

function CodeBootSpreadsheetEditor(elem, fe) {

    var se = this;

    se.elem = elem;
    se.fe = fe;

    var data = se.extractData(fe.file.content);

    se.firstLineIsHeaders = data.firstLineIsHeaders;

    var jsoptions = {
        data: data.rows,
        colHeaders: data.headers,
        colWidths: data.widths
    };

    se.jspreadsheet = jspreadsheet(elem, jsoptions);
}

CodeBootSpreadsheetEditor.prototype.getDelimiter = function () {

    var se = this;

    return (se.fe.file.getExtension() === '.tsv') ? '\t' : ',';
};

CodeBootSpreadsheetEditor.prototype.getValue = function () {

    var se = this;

    var delimiter = se.getDelimiter();

    var text = se.jspreadsheet.copy(false, delimiter, true, se.firstLineIsHeaders);

    return text.replace(/\r\n/g, '\n');
};

CodeBootSpreadsheetEditor.prototype.setValue = function (value) {

    var se = this;

    var data = se.extractData(value);

    se.firstLineIsHeaders = data.firstLineIsHeaders;

    var jsoptions = {
        data: data.rows,
        colHeaders: data.headers,
        colWidths: data.widths
    };

    se.elem.innerHTML = ''; // remove current spreadsheet element
    se.jspreadsheet = jspreadsheet(se.elem, jsoptions);
    se.fe.fileContainer.appendChild(se.elem);
};

CodeBootSpreadsheetEditor.prototype.extractData = function (value) {

    var se = this;

    var delimiter = se.getDelimiter();

    var table = jexcel.helpers.parseCSV(value, delimiter)

    function isNumber(x) {
        return x !== '' && !isNaN(+x);
    }

    function noNumbers(arr) {
        return !arr.some(isNumber);
    }

    var headers = null;
    var rows;

    if (table.length === 0) {
        rows = [['']];
    } else if (table.length === 1) {
        rows = table.slice();
    } else {
        if (noNumbers(table[0]) && !noNumbers(table[1])) {
            headers = table[0];
            rows = table.slice(1);
        } else {
            rows = table.slice();
        }
    }

    var firstLineIsHeaders = headers !== null;

    if (!firstLineIsHeaders) {
        headers = rows[0].map(function (x, i) {
            return se.defaultColumnName(i);
        });
    }

    var widths = rows[0].map(function (x, i) {
        function stringWidth(str) {
            return (str.length + 1) * 12 + 10;
        }
        var maxWidth = stringWidth(headers[i]);
        rows.forEach(function (row) {
            var cell = (i<row.length) ? row[i] : '';
            maxWidth = Math.max(maxWidth, stringWidth(cell));
        });
        return maxWidth;
    });

    return { rows: rows,
             headers: headers,
             firstLineIsHeaders: firstLineIsHeaders,
             widths: widths
           };
};

CodeBootSpreadsheetEditor.prototype.defaultColumnName = function (index) {

    var se = this;

    var name = '';

    index++;

    do {
        index--;
        name = String.fromCharCode(65+(index % 26)) + name;
        index = Math.floor(index/26);
    } while (index > 0);

    return name;
}

CodeBootFileEditor.prototype.setShowLineNumbers = function (show) {

    var fe = this;

    fe.textEditor.setOption('lineNumbers', show);
};

CodeBootFileEditor.prototype.refresh = function () {

    var fe = this;

    fe.textEditor.refresh();
};

// length of window (in ms) during which changes will be buffered
var SAVE_DELAY = 300;

CodeBootFileEditor.prototype.disable = function () {

    var fe = this;

    if (!fe.isEnabled()) return; // noop if currently not enabled

    var file = fe.file;

    file.fs.fem.remove(fe);
};

CodeBootFileEditor.prototype.rename = function () {

    var fe = this;
    var file = fe.file;
    var fs = file.fs;
    var vm = fs.vm;

    if (!fe.isEnabled()) return; // noop if currently not enabled

    var lastFocusedEditor = fe.file.fs.vm.lastFocusedEditor;
    fe.file.fs.vm.lastFocusedEditor = null; // allow focus to leave editor

    var oldFilename = fe.file.filename;
    var fileTab = fe.fileTab;
    var fileTabInput = fe.fileTabInput;
    var fileTabSpan  = fe.fileTabSpan;

    fileTabInput.value = oldFilename;

    function startEditing() {
        if (fileTabInput) {

            fileTab.setAttribute('data-cb-editing', '');

            fileTabInput.addEventListener('focusout', function (event) {
                doneRenaming();
            });

            fileTabInput.addEventListener('keydown', function (event) {
                if (event.keyCode === 27) {
                    event.stopPropagation();
                    resetTabToOldFilename();
                }
            });

            fileTabInput.addEventListener('keypress', function (event) {
                if (event.keyCode === 13) {
                    event.stopPropagation();
                    doneRenaming();
                }
            });

            fileTabInput.focus();

            fileTabInput.setSelectionRange(oldFilename.lastIndexOf('/')+1,
                                           oldFilename.length -
                                           fe.file.extension(oldFilename).length);
        }
    }

    function endEditing() {
        if (fileTabInput) {
            fileTab.removeAttribute('data-cb-editing');
            fileTabInput = null;
        }
    }

    function resetTabTo(filename) {
        endEditing();
        fe.setFilename(filename);
        fe.file.fs.vm.lastFocusedEditor = lastFocusedEditor;
        fe.file.fs.vm.focusLastFocusedEditor();
    }

    function resetTabToOldFilename() {
        endEditing();
        resetTabTo(oldFilename);
    }

    function doneRenaming() {
        if (fileTabInput) {

            var newFilename = fileTabInput.value;

            endEditing();

            if (newFilename !== oldFilename) {

                if (newFilename === '') {
                    resetTabToOldFilename();
                    vm.alertHTML(vm.polyglotHTML('Filename must not be empty'));
                    return;
                }

                if (fe.file.fs.hasFile(newFilename)) {
                    resetTabToOldFilename();
                    vm.alertHTML(vm.polyglotHTML('Filename must not be an existing file'));
                    return;
                }

                fe.file.fs.renameFile(oldFilename, newFilename);
            }

            resetTabTo(newFilename);
        }

        fe.file.fs.rebuildFileMenu();
    }

    startEditing();
};

CodeBootFileEditor.prototype.setReadOnly = function (readOnly) {

    var fe = this;

    fe.textEditor.setReadOnly(readOnly);
};

CodeBootFileEditor.prototype.setEditorView = function (view) {

    var fe = this;

    console.log('CodeBootFileEditor.prototype.setEditorView');

    fe.file.save(); // save in fe.file.content

    var currentContent = fe.getValue();

    fe.fileTab.setAttribute('data-cb-editor-view', view);
    fe.fileContainer.setAttribute('data-cb-editor-view', view);
    fe.currentEditorView = view;
    fe.file.preferredEditorView = view;

    if (fe.getValue() !== currentContent) {
        fe.setValue(currentContent);
    }

    fe.refresh();

    fe.file.fs.vm.focusLastFocusedEditor();
};

//-----------------------------------------------------------------------------

function endsWith(str, suffix) {
    return str.indexOf(suffix, str.length - suffix.length) !== -1;
}
