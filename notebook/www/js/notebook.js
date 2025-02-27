// THIS IS MINE

ready(onDeviceReady);

/* BEGIN: resize stuff */

var TOOLBAR_WIDTH = 48;
var SIDE_PANE_WIDTH = 480;

function onResize() {
    var toolbar = document.getElementById("toolbar");
    var main_window = document.getElementById("main-window");
    var main_area = document.getElementById("main-area");
    var divider = document.getElementById("divider");
    var right_pane = document.getElementById("right-pane");

    toolbar.style.height = window.innerHeight + 'px';
    main_area.style.height = window.innerHeight + 'px';
    main_area.style.height = window.innerHeight + 'px';
    right_pane.style.height = window.innerHeight + 'px';

    // Toolbar on the left, the rest is main_window
    toolbar.style.width = TOOLBAR_WIDTH + 'px';
    main_window.style.width = (window.innerWidth - TOOLBAR_WIDTH) + "px";

    var width = Math.ceil((window.innerWidth - TOOLBAR_WIDTH - $('#right-pane').width() - $('#divider').width()))-15; // WHY 15???
    var height = parseInt(main_area.style.height, 10);
    var canvas = document.getElementById("main-canvas");
    $(canvas).trigger('custom-resize-event', [height, width]);
}
/* END: resize stuff */


function onDeviceReady() {
    console.log("Check that console.log works.");

    $("#main-window").on('splitpaneresize', function (evt) {
        onResize();
    });

    
    /* Controller stuff on canvas */
    var canvas = document.getElementById("main-canvas");
    editor = new Editor(canvas);

    var notebook_name = window.location.pathname.split("/")[2];    
    editor.load_notebook(get_notebook_name_from_url(), get_page_number_from_url());

    
    /* Begin resize stuff */
    $(function() { $('div.split-pane').splitPane(); });
    window.onresize = onResize;
    onResize();
    /* End resize stuff */
}
