// THIS IS MINE


function simplify_path(path) {
    // turn [M,Q,L... ] -> [{x:, y:}]
    //console.log(path)
    var points = []
    for (i in path['path']) {
        //console.log(i, path['path'][i]);

        if (path['path'][i][0]=='M') {
            points.push({x: path['path'][i][1], y: path['path'][i][2]})
        }
        if (path['path'][i][0]=='L') {
            points.push({x: path['path'][i][1], y: path['path'][i][2]})
        }
        if (path['path'][i][0]=='Q') {
            points.push({x: path['path'][i][1], y: path['path'][i][2]})
            points.push({x: path['path'][i][3], y: path['path'][i][4]})
        }
    }

    //simplify
    //console.log('Initial length (path, points):', path['path'].length, points.length);
    var points2 = simplify(points, tolerance=1);
    //console.log('simplified length (path, points):', path['path'].length, points2.length);
    //console.log('simplified from ', points.length, ' to ',  points2.length, ' i.e. ', 100*points2.length/points.length, '%')
    points = points2;
    // turn [{x:, y:}] -> [M,Q,L... ]
    var path2 = {path: []}
    path2['path'].push(['M', points[0]['x'], points[0]['y']])
    for (i=0; i<(points.length-2)/2; i++) {
        path2['path'].push(['Q', points[2*i]['x'], points[2*i]['y'], points[2*i+1]['x'], points[2*i+1]['y']]);
    }
    path2['path'].push(['L', points[points.length-1]['x'], points[points.length-1]['y']]);
    path['path'] = path2['path'];    
    return path;
}

/*

0 (3) ["M", 232.85125455279191, 484.0487236436873]
reader.js:5 1 (5) ["Q", 232.85125455279191, 484.0487236436873, 233.35125455279191, 484.0487236436873]
reader.js:5 2 (5) ["Q", 233.85125455279191, 484.0487236436873, 235.00358514403322, 482.8467107015912]
reader.js:5 3 (5) ["Q", 236.15591573527453, 481.6446977594951, 240.56324045060438, 478.23899442355616]
reader.js:5 4 (5) ["Q", 244.97056516593423, 474.83329108761717, 265.60485815134217, 461.01014225351196]
reader.js:5 5 (5) ["Q", 286.23915113675014, 447.18699341940675, 307.4744429469757, 433.96485105634963]
reader.js:5 6 (5) ["Q", 328.7097347572014, 420.74270869329246, 348.34236303457976, 408.1215728012834]
reader.js:5 7 (5) ["Q", 367.9749913119582, 395.50043690927436, 376.38897485940606, 389.29003670844446]
reader.js:5 8 (5) ["Q", 384.802958406854, 383.07963650761457, 388.20861841415433, 380.27493964272367]
reader.js:5 9 (5) ["Q", 391.6142784214546, 377.4702427778328, 394.41893960393725, 375.26655238398996]
reader.js:5 10 (5) ["Q", 397.2236007864199, 373.06286199014704, 399.4272631440848, 371.4601780673522]
reader.js:5 11 (5) ["Q", 401.63092550174974, 369.85749414455745, 402.63259020977927, 368.85581669281066]
reader.js:5 12 (5) ["Q", 403.6342549178088, 367.85413924106393, 404.0349208010206, 367.45346826036524]
reader.js:5 13 (5) ["Q", 404.4355866842324, 367.05279727966655, 404.4355866842324, 367.05279727966655]
reader.js:5 14 (5) ["Q", 404.4355866842324, 367.05279727966655, 404.4355866842324, 367.05279727966655]


*/





function init() {
    self = this;
    self.page_number = 1;
    
    // add a css pointer-events: none; when a swipe is detected??

    // Size is weird - it's fine before Fabric, broken after, so we save/reload it
    var canvas = document.getElementById("main-canvas");
    var width = $(canvas).width()
    var height = $(canvas).height()
    var fcanvas = new fabric.StaticCanvas('main-canvas');
    $(canvas).on("custom-resize-event", function(evt, height, width) {
        fcanvas.setWidth(Math.floor(width));
        fcanvas.setHeight(Math.floor(height));
        fcanvas.calcOffset();
    });
    $(canvas).trigger('custom-resize-event', [height, width]);

    // don't want to draw selection marquee - just pan?
    fcanvas.selection = false;
    fcanvas.isDrawingMode = false;

    get_max_pages(function(num_pages) {
        self.num_pages = num_pages;
    });

    self.pagebus = new Bacon.Bus();
    self.pagebus.onValue(function(value) {
        self.page_number = value;
        var notebook_name = get_notebook_name_from_url();
        self.load_notebook(notebook_name, self.page_number);
    });
    self.pagebus.log()

    self.load_notebook = function(notebook_name, page_number) {
        console.log('LOAD:', notebook_name, page_number);
        self.loading_in_progress = true;
        fcanvas.clear();
        self.keep_unselectable = [];
        draw_lined_page(fcanvas, self.keep_unselectable);

        $.get('/get-notebook-data/' + notebook_name + '/' + page_number, null, function(result) {
            set_page_number_url(page_number);
            self.page_number = page_number;
            var json = JSON.parse(result);
            var json2 = JSON.parse(json);
            fcanvas.renderOnAddRemove=false;

            // attempt to simplify
            for (i in json2['objects']) {
                if (json2['objects'][i]['type']=='path') {
                    json2['objects'][i] = simplify_path(json2['objects'][i]);
                }
            }
            
            fabric.Group.fromObject(json2, function(obj) {
                var g = new fabric.Group();
                fcanvas.add(g);
                for(i in obj._objects) {
                    g.add(obj._objects[i])
                }
                g.addWithUpdate();
                g.setCoords();
                fcanvas.renderAll();

                //for(i in obj._objects) {
                //    fcanvas.add(obj._objects[i])
                //}
            });
            fcanvas.renderOnAddRemove=true;
            reset_coords(fcanvas);
            self.loading_in_progress = false;
            fcanvas.renderAll();
            
        }); // get-notebook-data        
    } // load_notebook
    
    var el = document.getElementById('main-canvas');
    var hammertime = new Hammer(el, {});
    //hammertime.get('pinch').set({ enable: true });
    hammertime.get('pan').set({ direction: Hammer.DIRECTION_ALL, threshold: 1 });
    hammertime.get('swipe').set({ direction: Hammer.DIRECTION_HORIZONTAL, threshold: 20, velocity: 0.3});
    hammertime.get('tap').set({ taps: 2 });
    
    /*
      fcanvas.on('mouse:wheel', function(opt) {
        if (opt.e.altKey === true) {
            var delta = opt.e.deltaY;
            var zoom = fcanvas.getZoom();
            zoom *= 0.999 ** delta;
            var min_zoom_x = fcanvas.getWidth() / CONSTANTS.PAPER_WIDTH;
            var min_zoom_y = fcanvas.getHeight() / CONSTANTS.PAPER_HEIGHT;
            var min_zoom = Math.max(min_zoom_x, min_zoom_y);
            if (zoom > 20) zoom = 20;
            if (zoom < min_zoom) {
                zoom = min_zoom;
            }
            fcanvas.zoomToPoint({ x: opt.e.offsetX, y: opt.e.offsetY }, zoom);
            reset_coords(fcanvas);
            opt.e.preventDefault();
            opt.e.stopPropagation();
            limit_panning(fcanvas);
        } else {
            var vpt = this.viewportTransform;
            vpt[4] -= opt.e.deltaX;
            vpt[5] -= opt.e.deltaY;
            limit_panning(fcanvas);
        }
        this.setViewportTransform(this.viewportTransform);
        reset_coords(fcanvas);
    });
    //scale = Math.max(1, Math.min(last_scale * ev.gesture.scale, 10));
    function zoom(delta, x, y) {
        var zoom = fcanvas.getZoom();
        zoom *= 0.999 ** delta;
        console.log(fcanvas.getZoom(), zoom)        
        var min_zoom_x = fcanvas.getWidth() / CONSTANTS.PAPER_WIDTH;
        var min_zoom_y = fcanvas.getHeight() / CONSTANTS.PAPER_HEIGHT;
        var min_zoom = Math.max(min_zoom_x, min_zoom_y);
        if (zoom > 20) zoom = 20;
        if (zoom < min_zoom) {
            zoom = min_zoom;
        }
        fcanvas.zoomToPoint({ x: x, y: y }, zoom);
        reset_coords(fcanvas);
        limit_panning(fcanvas);
    }
    hammertime.on('pinchin', function(ev) {
	console.log('pinchin', ev);
        //zoom(1/ev.scale * 60, ev.center.x, ev.center.y)
    });
    hammertime.on('pinchout', function(ev) {
	console.log('pinchout', ev);
        //zoom(-1 * ev.scale * 60, ev.center.x, ev.center.y)
    });
    */




    //var manager = new Hammer.Manager();
    // Create a recognizer
    //var DoubleTap = new Hammer.Tap({
    //event: 'doubletap',
    //  taps: 2
    //});

    // Add the recognizer to the manager
    //manager.add(DoubleTap);

    // Subscribe to desired event

    var DEFAULT_ZOOM = 0.17;
    var zoomlevel = 0;
    hammertime.on('doubletap', function(ev) {
        console.log('double tap', zoomlevel, ev.center.x, ev.center.y);
        var zoom;
        if (zoomlevel==0) {
            zoom = 0.5;
            zoomlevel = 1;
        } else if (zoomlevel==1) {
            zoom = DEFAULT_ZOOM;
            zoomlevel = 0;
        }
        fcanvas.zoomToPoint({ x: ev.center.x, y: ev.center.y }, zoom);
        limit_panning(fcanvas);
    });


    // Pan seems to work if a bit slow
    hammertime.on('panstart', function(ev) {
        //console.log(ev.type, ev.center.x, ev.center.y, ev.deltaX, ev.deltaY);
        self.lastPosX = ev.center.x;
        self.lastPosY = ev.center.y;
    });
    
    hammertime.on('pan', function(ev) {
	//console.log(ev.type, ev.center.x, ev.center.y, ev.deltaX, ev.deltaY);
        var vpt = fcanvas.viewportTransform;
        //console.log(vpt);
        vpt[4] += ev.center.x - self.lastPosX;
        vpt[5] += ev.center.y - self.lastPosY;
        limit_panning(fcanvas);
        self.lastPosX = ev.center.x;
        self.lastPosY = ev.center.y;
        fcanvas.setViewportTransform(fcanvas.viewportTransform);
        reset_coords(fcanvas);
        
    });
    hammertime.on('panend', function(ev) {

    });

    // swipe left/right to go forward and back 
    hammertime.on('swipeleft', function(ev) {
        var pageno = self.page_number + 1;
        if (pageno > self.num_pages) {
            pageno = self.num_pages;
        }
        self.pagebus.push(pageno);
    });

    hammertime.on('swiperight', function(ev) {
        var pageno = self.page_number - 1;
        if (pageno < 1) {
            pageno = 1;
        }        
        self.pagebus.push(pageno);
    });

    var unselectable = []
    draw_lined_page(fcanvas, unselectable);
    fcanvas.zoomToPoint({ x: 0, y: 0 }, DEFAULT_ZOOM);

    var notebook_name = window.location.pathname.split("/")[2];
    self.load_notebook(get_notebook_name_from_url(), get_page_number_from_url());

    
}
