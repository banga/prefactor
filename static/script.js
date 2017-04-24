const $source = $("#source");
const $visitor = $("#visitor");
const $tree = $("#tree");
const $output = $("#output");
const $arrow = $("<div>➡</div>").addClass("error-arrow");
const $save = $("#save");
const $load = $("#load");
const $stateName = $("#stateName");
const $stateList = $("#stateList");
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
    highlightLineNodes(cursor.line + 1);
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
const kDefaultState = "default";

function updateTree() {
    const state = saveState(kDefaultState);
    updateOutput();
    parseApi({source: state.source},
        function(data) {
            console.log(data.tree);
            $tree.html("").append(renderNode(data.tree));
            updateHighlightedLineNodes();
        });
}

function updateOutput() {
    const gutterId = "CodeMirror-linenumbers";
    const state = saveState(kDefaultState);
    transformApi(
        {source: state.source, visitor: state.visitor},
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

function stateName(name) {
    return "state-" + name;
}

function saveState(name) {
    var source = sourceEditor.getValue();
    var visitor = visitorEditor.getValue();
    var state = {
        source: source,
        visitor: visitor
    };
    storage[stateName(name)] = JSON.stringify(state);
    updateStateList();
    return state;
}

function getState(name) {
    if (!(stateName(name) in storage)) {
        return;
    }
    return JSON.parse(storage[stateName(name)]);
}

function loadState(name) {
    var state = getState(name);
    if (!state) {
        console.warn(`State ${name} not found`);
        return;
    }
    sourceEditor.setValue(state.source);
    visitorEditor.setValue(state.visitor);
}

function updateStateList() {
    $stateList.html("");
    for (var key in storage) {
        if (key.startsWith("state-")) {
            var name = key.split("-")[1];
            $stateList.append($("<option>").val(name).html(name));
        }
    }
}

function initialize() {
    updateStateList();
    sourceEditor = makeEditor("", $source);
    sourceEditor.on("cursorActivity", updateHighlightedLineNodes);
    sourceEditor.on("changes", updateTree);

    visitorEditor = makeEditor("", $visitor);
    visitorEditor.on("changes", updateOutput);

    $save.click(function() {
        const name = $stateName.val() || kDefaultState;
        saveState(name);
    });

    $load.click(function() {
        const name = $stateName.val() || kDefaultState;
        loadState(name);
    });

    loadState(kDefaultState);
}

initialize();