// THIS IS MINE

var CONSTANTS = {
    TOP_MARGIN: 236,
    BOTTOM_MARGIN: 94,
    LINE_SPACING: 94,
    PAPER_WIDTH: 2480, PAPER_HEIGHT: 3507, // A4
    
    MINI_PAGE_WIDTH: 180,
    MINI_PAGE_HEIGHT: 254,
    
}


function ready(fn) {
    if (document.readyState != 'loading'){
        fn();
    } else {
        document.addEventListener('DOMContentLoaded', fn);
    }
}



function draw_lined_page(fcanvas, unselectable) {
    var rect = new fabric.Rect({
        left: 0,
        top: 0,
        fill: '#ffffff',
        width: CONSTANTS.PAPER_WIDTH,
        height: CONSTANTS.PAPER_HEIGHT
    });
    rect.selectable = false
    rect.toSVG = function() { return ''; };
    rect.toJSON = function() { return ''; };
    rect.toObject = function() { return ''; };
    fcanvas.add(rect);
    unselectable.push(rect);
    
    var lined_page_height = CONSTANTS.PAPER_HEIGHT - CONSTANTS.TOP_MARGIN - CONSTANTS.BOTTOM_MARGIN
    var num_lines = lined_page_height / CONSTANTS.LINE_SPACING
    for (i = 0; i < num_lines; i++) {
        var top = CONSTANTS.TOP_MARGIN + i * CONSTANTS.LINE_SPACING;
        line = new fabric.Line([0, top, CONSTANTS.PAPER_WIDTH, top], {stroke: 'blue'})
        line.selectable = false
        line.toSVG = function() { return ''; };
        line.toJSON = function() { return ''; };
        line.toObject = function() { return ''; };
        fcanvas.add(line);
        unselectable.push(line);
    }
} // draw_lined_page

function get_notebook_name_from_url() {
    return window.location.pathname.split("/")[2];
}

function get_page_number_from_url() {
    var page_number = window.location.hash.substr(1);
    if (page_number==""){
        page_number = 1;
    } else {
        page_number = parseInt(page_number);
    }
    console.log("pagenumber:"+page_number+"...");
    return page_number;
}


function set_page_number_url(page_number) {
    window.location.hash = '#' + page_number;
}


function get_max_pages(callback) {
    var notebook_name = get_notebook_name_from_url();
    $.get('/get-notebook-num-pages/' + notebook_name, null, function(result) {
        var num_pages = JSON.parse(result);
        callback(num_pages);
    }); // get-notebook-data
}

function reset_coords(fcanvas) {
    fcanvas.getObjects().forEach(function(obj) {
        obj.setCoords();
    });
}


function limit_panning(fcanvas) {
    var vpt = fcanvas.viewportTransform;
    // left
    if (vpt[4] > 0) {
        vpt[4] = 0;
    }
    // top
    if (vpt[5] > 0) {
        vpt[5] = 0;
    }
    var zoom = fcanvas.getZoom();
    var window_width = $('#main-area').width();
    var window_height = $('#main-area').height();
    //top
    var min_offset_x = -1*(zoom*CONSTANTS.PAPER_WIDTH-window_width);
    if (vpt[4] < min_offset_x) {
        vpt[4] = min_offset_x;
    }
    // bottom
    var min_offset_y = -1*(zoom*CONSTANTS.PAPER_HEIGHT-window_height);
    if (vpt[5] < min_offset_y) {
        vpt[5] = min_offset_y;
    }
    fcanvas.renderAll();
    reset_coords(fcanvas);
};










