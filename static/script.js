const $source = $("#source");
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

var lastRequest;
function updateOutput() {
    if (lastRequest) {
        lastRequest.abort();
    }
    lastRequest = $.ajax({
        type: "POST",
        url: "/parse",
        data: {source: $source.val()},
        success: function(data) {
            console.log(data.tree);
            $output.html("").append(renderNode(data.tree));
            updateHighlightedLineNodes();
        },
        dataType: "json"
    });
}

$source.on("click", updateHighlightedLineNodes);
$source.on("keyup", updateHighlightedLineNodes);
$source.on("input", updateOutput);
updateOutput();