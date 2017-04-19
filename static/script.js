const $source = $("#source");
const $visitor = $("#visitor");
const $tree = $("#tree");
const $output = $("#output");
const $arrow = $("<div>➡</div>").addClass("error-arrow");
var sourceEditor;
var visitorEditor;
var outputEditor;

function renderNode(node) {
    const div = $("<div>")
        .addClass("node")
        .addClass(node.type)
        .attr("data-lineno", node.lineno);

    if (node.type) {
        div.append($("<span>")
            .addClass("type")
            .toggleClass("terminal", node.is_terminal)
            .toggleClass("non_terminal", !node.is_terminal)
            .text(node.type));
    }
    if (node.value) {
        div.append($("<span>")
            .addClass("value")
            .text(`"${node.value}"`));
    }
    if (node.prefix) {
        div.append($("<span>")
            .addClass("prefix")
            .text(`prefix="${node.prefix}"`));
    }
    if (node.children) {
        const children = $("<div>")
            .addClass("children");
        node.children.forEach(function(child) {
            children.append(renderNode(child));
        });
        div.append(children);
    }
    return div;
}

function highlightLineNodes(lineno) {
    $(".node").removeClass("highlight");
    if (lineno) {
        const $highlighted = $(`.node[data-lineno="${lineno}"`)
            .addClass("highlight");
        $(".node.highlight .highlight").removeClass("highlight");
        if ($highlighted.get(0)) {
            $highlighted.get(0).scrollIntoViewIfNeeded();
        }
    }
}

function updateHighlightedLineNodes() {
    const cursor = sourceEditor.getCursor();
    highlightLineNodes(cursor.line);
}

function makeEditor(value, node) {
    var options = {
        value: value,
        mode: {
            name: "python",
            version: 3,
        },
        lineNumbers: true,
        indentUnit: 4,
        viewportMargin: Infinity
    };
    return CodeMirror(function(elt) {
        node.html("");
        node.append(elt);
    }, options);
}

function apiCall(endpoint) {
    var request = null;
    return function(data, success) {
        if (request) {
            request.abort();
        }
        request = $.ajax({
            type: "POST",
            url: endpoint,
            data: data,
            success: success,
            dataType: "json"
        });
    };
}

const parseApi = apiCall("/parse");
const transformApi = apiCall("/transform");
const storage = localStorage;

function updateTree() {
    storage.source = sourceEditor.getValue();
    updateOutput();
    parseApi({source: storage.source},
        function(data) {
            console.log(data.tree);
            $tree.html("").append(renderNode(data.tree));
            updateHighlightedLineNodes();
        });
}

function updateOutput() {
    const gutterId = "CodeMirror-linenumbers";

    storage.visitor = visitorEditor.getValue();
    transformApi(
        {source: storage.source, visitor: storage.visitor},
        function(data) {
            console.log(data);
            visitorEditor.getDoc().clearGutter(gutterId);
            if (data.output) {
                outputEditor = makeEditor(data.output, $output);
            } else {
                visitorEditor.getDoc().setGutterMarker(
                    data.error.lineno - 1, gutterId, $arrow.get(0));
                $output.html(`${data.error.message} on line ` +
                    `${data.error.lineno}`);
            }
        });
}

function initialize() {
    sourceEditor = makeEditor(storage.source, $source);
    sourceEditor.on("cursorActivity", updateHighlightedLineNodes);
    sourceEditor.on("changes", updateTree);

    visitorEditor = makeEditor(storage.visitor, $visitor);
    visitorEditor.on("changes", updateOutput);

    updateTree(sourceEditor);
}

initialize();