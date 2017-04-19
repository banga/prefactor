const $source = $("#source");
const $visitor = $("#visitor");
const $tree = $("#tree");
const $output = $("#output");

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
    const lineno = $source.val().substr(
        0, $source.get(0).selectionStart).split("\n").length;
    highlightLineNodes(lineno);
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
    storage.source = $source.val();
    updateOutput();
    parseApi(
        {source: $source.val()},
        function(data) {
            console.log(data.tree);
            $tree.html("").append(renderNode(data.tree));
            updateHighlightedLineNodes();
        });
}

function updateOutput() {
    storage.visitor = $visitor.val();
    transformApi(
        {source: $source.val(), visitor: $visitor.val()},
        function(data) {
            console.log(data);
            if (data.output) {
                $output.html(data.output);
                $output.removeClass("error");
            } else {
                $output.html(`${data.error.message} on line ` +
                    `${data.error.lineno}`);
                $output.addClass("error");
            }
        });
}

function initialize() {
    $source.on("click", updateHighlightedLineNodes);
    $source.on("keyup", updateHighlightedLineNodes);
    $source.on("input", updateTree);
    $visitor.on("input", updateOutput);

    $source.val(storage.source || "");
    $visitor.val(storage.visitor || "");
    updateTree();
}

initialize();