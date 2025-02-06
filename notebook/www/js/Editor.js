
// THIS IS MINE


function getBase64Image(img) {
    var canvas = document.createElement("canvas");
    canvas.width = img.width;
    canvas.height = img.height;
    var ctx = canvas.getContext("2d");
    ctx.drawImage(img, 0, 0);
    var dataURL = canvas.toDataURL("image/png");
    return dataURL.replace(/^data:image\/(png|jpg);base64,/, "");
}




function Editor(canvas) {
    var self = this;
    self.tool = 'pan';
    self.pensize = 1;

    self.page_number = 1;
    self.loading_in_progress = false;
    self.keep_unselectable = []
    self.max_page = 0;

    function get_selection(fcanvas){
        return fcanvas.getActiveObject() == null ? fcanvas.getActiveGroup() : fcanvas.getActiveObject()
    }
    
    function select_all(fcanvas) {
        var objs = fcanvas.getObjects().map(function(o) { return o.set('active', true); });
        var group = new fabric.Group(objs, { originX: 'center', originY: 'center' });
        fcanvas._activeObject = null;
        fcanvas.setActiveGroup(group.setCoords()).renderAll();
    }

    self.copy = function() {
        selection = get_selection(fcanvas);
        self.clipboard_json = JSON.stringify({'objects':[selection.toJSON()]});
        localStorage.setItem("clipboard_json", self.clipboard_json);
    }

    self.cut = function() {
        self.copy();
        selection = fcanvas.getActiveObject();
        if (selection!= null) {
            fcanvas.remove(selection);
        } else {
            selection = fcanvas.getActiveGroup();
            selection = fcanvas.getActiveGroup().getObjects();;
            fcanvas.discardActiveGroup();
            for (i in selection) {
                fcanvas.remove(selection[i])
            }
        }
    }

    self.paste = function() {
        self.clipboard_json = localStorage.getItem("clipboard_json");
        fcanvas2.loadFromJSON(self.clipboard_json, fcanvas2.renderAll.bind(fcanvas2));
        select_all(fcanvas2);
        get_selection(fcanvas2).clone(function(cloned) {
            self.clipboard = cloned;
            self.clipboard.clone(function(clonedObj) {
                fcanvas.discardActiveObject();
                var zoom = fcanvas.getZoom();
                var vpt = fcanvas.viewportTransform;
                var left = parseInt(fcanvas.getWidth() / 2.0) / zoom - vpt[4]/zoom;
                var top = parseInt(fcanvas.getHeight() / 2) / zoom - vpt[5]/zoom;
                clonedObj.set({ left: left, top: top, evented: true });
                if (clonedObj.type === 'activeSelection') {
                    clonedObj.canvas = fcanvas;
                    clonedObj.forEachObject(function(obj) {
                        console.log('multiple: ', obj)
                        fcanvas.add(obj);
                    });
                    clonedObj.setCoords();
                } else {
                    fcanvas.add(clonedObj);
                }
                self.clipboard.top += 10;
                self.clipboard.left += 10;
                fcanvas.setActiveObject(clonedObj);

            }); // clone from clipboard
        }); // clone from canvas 2
    } // self.paste

    this.init = function() {   
        self.toolbus = new Bacon.Bus();
        self.toolbus.onValue(function(value) {
            // set class to make the button appear pushed
            $("#tool-" + self.tool).removeClass('active');
            self.tool = value;
            $("#tool-" + self.tool).addClass('active');
            // Is free drawing?
            if (self.tool=='draw-free') {
                fcanvas.isDrawingMode = true;
                $('.upper-canvas').addClass('dotcursor');
            } else {
                fcanvas.isDrawingMode = false;
                $('.upper-canvas').removeClass('dotcursor');
            }
            if (self.tool == 'select') {
                fcanvas.forEachObject(function(object){
                    if (self.keep_unselectable.includes(object)==false) {
                        object.selectable = true;
                    }
                });
            }
            if (self.tool == 'pan') {
                fcanvas.forEachObject(function(object){ 
                    object.selectable = false; 
                });
            }
            if (self.tool == 'insert-text') {
                var zoom = fcanvas.getZoom();
                var vpt = fcanvas.viewportTransform;
                var left = parseInt(fcanvas.getWidth() / 2.0) / zoom - vpt[4]/zoom;
                var top = parseInt(fcanvas.getHeight() / 2) / zoom - vpt[5]/zoom;
                var text = new fabric.Textbox('hello world', { left: left, top: top });
                fcanvas.add(text);
            }
        }); // toolbus.onValue

        self.pagebus = new Bacon.Bus();
        self.pagebus.onValue(function(value) {
            $(".small-page").removeClass('active-page');
            self.page_number = value;
            $("#page-" + self.page_number).addClass('active-page');
            var notebook_name = get_notebook_name_from_url();
            self.load_notebook(notebook_name, self.page_number);
        });
        self.pagebus.log()

        self.pensizebus = new Bacon.Bus();
        self.pensizebus.log();
        $('#size-1').on('click', function (evt) { self.pensizebus.push(1); });
        $('#size-2').on('click', function (evt) { self.pensizebus.push(2); });
        $('#size-3').on('click', function (evt) { self.pensizebus.push(3); });
        $('#size-4').on('click', function (evt) { self.pensizebus.push(4); });
        self.pensizebus.onValue(function(value) {
            $("#size-" + self.pensize).removeClass('small-toolbar-button-active');
            self.pensize = value;
            $("#size-" + self.pensize).addClass('small-toolbar-button-active');
        });

        $('#tool-pan').on('click', function (evt) { self.toolbus.push('pan'); });
        $('#tool-zoom').on('click', function (evt) { self.toolbus.push('zoom'); });
        $('#tool-zoom-reset').on('click', function (evt) { });
        $('#tool-select').on('click', function (evt) { self.toolbus.push('select'); });
        $('#tool-lasso-select').on('click', function (evt) { self.toolbus.push('lasso-select'); });
        $('#tool-draw-free').on('click', function (evt) { self.toolbus.push('draw-free'); });
        $('#tool-draw-line').on('click', function (evt) { self.toolbus.push('draw-line'); });
        $('#tool-draw-rectangle').on('click', function (evt) { self.toolbus.push('draw-rectangle'); });
        $('#tool-draw-circle').on('click', function (evt) { self.toolbus.push('draw-circle'); });
        $('#tool-insert-text').on('click', function (evt) { self.toolbus.push('insert-text'); });
        $('#tool-insert-image').on('click', function (evt) { self.toolbus.push('insert-image'); });
        $('#tool-area-eraser').on('click', function (evt) { self.toolbus.push('area-eraser'); });
        $('#tool-lasso-eraser').on('click', function (evt) { self.toolbus.push('lasso-eraser'); });
        $('#tool-undo').on('click', function (evt) {  });
        $('#tool-redo').on('click', function (evt) {  });


        //$('#tool-next-page').on('click', function (evt) {  });
        //$('#tool-previous-page').on('click', function (evt) { });

    } // this.init

    var fcanvas = new fabric.Canvas('main-canvas', {preserveObjectStacking: true});
    var fcanvas2 = new fabric.Canvas('canvas2', {preserveObjectStacking: true});
    
    $(canvas).on("custom-resize-event", function(evt, height, width) {
        //console.log('Editor: custom-resize-event', height, width, Math.floor(height), Math.floor(width));
        fcanvas.setWidth(Math.floor(width));
        fcanvas.setHeight(Math.floor(height));
        fcanvas.calcOffset();
    });

    
    fcanvas.on('mouse:down', function(options) {
        //console.log(options.e.clientX, options.e.clientY, options.target);        
    });

    $('#tool-cut').on('click', function() {
        self.cut();
    });
    $('#tool-copy').on('click', function() {
        self.copy();
    });
    $('#tool-paste').on('click', function() {
        self.paste();
    });


    
    fcanvas.on('mouse:wheel', function(opt) {
        if (opt.e.altKey === true) {
            var delta = opt.e.deltaY;
            console.log(delta);
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

    // Pan tool
    fcanvas.on('mouse:down', function(opt) {
        if (self.tool == 'pan') {
            self.isDragging = true;
            this.selection = false;
            this.lastPosX = opt.e.clientX;
            this.lastPosY = opt.e.clientY;
        }
    });
    fcanvas.on('mouse:move', function(opt) {
        if (self.isDragging) {
            var vpt = this.viewportTransform;
            vpt[4] += opt.e.clientX - this.lastPosX;
            vpt[5] += opt.e.clientY - this.lastPosY;
            limit_panning(fcanvas);
            this.lastPosX = opt.e.clientX;
            this.lastPosY = opt.e.clientY;
            reset_coords(fcanvas);
        }
    });
    fcanvas.on('mouse:up', function(opt) {
        this.setViewportTransform(this.viewportTransform);
        reset_coords(fcanvas);
        self.isDragging = false;
        this.selection = true;
    });
    

    this.load_notebook = function(notebook_name, page_number) {
        console.log('Attempt load: ', notebook_name, page_number);
        self.loading_in_progress = true;
        //self.pagebus.push(page_number); ------- this causes an infinite loop
        fcanvas.clear();
        self.keep_unselectable = [];
        draw_lined_page(fcanvas, self.keep_unselectable);

        $.get('/get-notebook-data/' + notebook_name + '/' + page_number, null, function(result) {
            set_page_number_url(page_number);
            self.page_number = page_number;
            var json = JSON.parse(result);
            var json2 = JSON.parse(json);
            fabric.Group.fromObject(json2, function(obj) {
                fcanvas.renderOnAddRemove=false;
                for(i in obj._objects) {
                    fcanvas.add(obj._objects[i])                    
                    // on startup we're in pan mode - maybe this needs to be abstracted out into an event bus or something
                    if (self.tool=='pan') {
                        obj._objects[i].selectable = false; 
                    }
                }
                fcanvas.renderOnAddRemove=true;
            });
            reset_coords(fcanvas);
            self.loading_in_progress = false;
            
            $("#page-" + self.page_number).addClass('active-page');
        }); // get-notebook-data
    } // load notebook

    self.save_notebook = function() {
        console.log('saving...');
        var notebook_name = window.location.pathname.split("/")[2];
        var page_number = window.location.hash.substr(1);
        console.log('notebook_name:', notebook_name, page_number)
        var objects = fcanvas.toObject();
        var new_objects = {objects: []}
        for(i in objects['objects']) {
            if (objects['objects'][i] !="") {
                new_objects.objects.push(objects['objects'][i]);
            }
        }
        $.post('/set-notebook-data/' + notebook_name + '/' + page_number, JSON.stringify(new_objects), function(success){
            console.log('saved...')
        }, 'json');

    }

    var page_click_handler = function (evt) {
        if (evt.target.id == "new-page") {
            return;
        }
        var value = parseInt(evt.target.id.split('-')[1]);
        if (value != self.page_number) {
            self.pagebus.push(value);
        }
    }

    var little_page = function(i){
        return $('<div id="page-' + i + '" class="small-page unselectable">' + i +'</div>')
    }
    
    self.draw_num_pages = function() {
        get_max_pages(function(num_pages) {
            console.log('num_pages:', num_pages);
            for (i=0; i<num_pages; i++) {
                var page = little_page(i + 1);
                $("#new-page").before(page);
                self.max_page = i+1;
            }
            $('.small-page').on('click', page_click_handler);
        });
    } // draw_num_pages
    self.draw_num_pages();

    $('#new-page').click(function() {
        self.max_page = self.max_page + 1;
        var page = little_page(self.max_page);
        $("#new-page").before(page);
        $(page).on('click', page_click_handler);
        var notebook_name = get_notebook_name_from_url();
        self.load_notebook(notebook_name, self.max_page);

    })

    // detect changes
    self.changebus = new Bacon.Bus();
    fcanvas.on('object:modified', function(opt) {
        self.changebus.push('object:modified');
    });
    fcanvas.on('object:added', function(opt) {
        self.changebus.push('object:added');
    });
    fcanvas.on('object:removed', function(opt) {
        console.log('removed: self.loading_in_progress=', self.loading_in_progress);
        self.changebus.push('object:removed');
    });
    self.changebus.debounce(2).onValue(function(value) {
        //
        if (self.loading_in_progress==false) {
            //console.log('changebus (value, loading_in_progress):', value);
            self.save_notebook();
        }
    });
    
    this.init();
    fcanvas.zoomToPoint({ x: 0, y: 0 }, 0.484);
    reset_coords(fcanvas);
    //fcanvas.zoomToPoint({ x: 0, y: 0 }, 1.0);

    // paste image from clipboard
    window.addEventListener("paste", function(evt){
        var items = evt.clipboardData.items;
        var blob = items[0].getAsFile();
        var img = new Image();
        img.onload = function(){
            console.log('img loaded');
            var img_data = getBase64Image(img);
            console.log(img_data);
            notebook_name = get_notebook_name_from_url();
            $.post("/put-image", JSON.stringify({'data': img_data, 'notebook': notebook_name}), function(data) {
              fabric.Image.fromURL(data, function(myImg) {
                  var img1 = myImg.set({ left: 0, top: 0 ,width:150,height:150});
                  fcanvas.add(img1); 
              }); // add to canvas
            }); // put on server            
        }; // img on load
        var URLObj = window.URL || window.webkitURL;
        img.src = URLObj.createObjectURL(blob);
        console.log('img.src:', img.src);
    }, false); // paste event



    // links: https://github.com/fabricjs/fabric.js/issues/3518#issuecomment-685783342
    fcanvas.on('mouse:down', function(opt) {
        if (self.tool=='pan') {
            if (opt.target) {
                console.log('an object was clicked! ', opt.target.type);
                if (opt.target.type == 'textbox'){
                    if (opt.target.text.substring(0,4)=='http') {
                        window.open(opt.target.text);
                        self.isDragging = false;
                    }
                }
                //var pointClicked = opt.target.canvas.getPointer(opt.e);
                //console.log(pointClicked);
                //if(opt.target.id){
                // if you set an ID you can use it in a switch or if command it worth noting you have to
                // tell it to keep id's when using canvas.toJSON() like this canvas.toJSON(['id'])
                //console.log('ID:', opt.target.id);
                //}
            }// target
        }// panning
    });

    // http://fabricjs.com/freedrawing
    fcanvas.freeDrawingBrush.width = 4;



    
}
