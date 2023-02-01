odoo.define('website_pdf_preview.frontend', function (require) {
"use strict";

	var rpc = require('web.rpc');
	var core = require('web.core');
	var QWeb = core.qweb;
	var session = require('web.session');
	var ajax = require('web.ajax');

	$(document).ready(function(){
		var $anchor_attachments = $('a')
		var pdfDoc = null,
	    pageNum = 1,
	    pageRendering = false,
	    pageNumPending = null,
	    scale = 1.0,
	    rotation = 0,
		canvas = false,
	    ctx = false;
		_.each($anchor_attachments,function(key){
			var a_href = $(key).attr('href')
			if(a_href && a_href.includes("/web/content")) {
				$(key).addClass('pdf_preview')
			}
		})
		
		function renderAllPage() {
			var max_page = pdfDoc.numPages;
			var i=1;
			while(i <= max_page) {
				var temp_canvas = document.createElement('canvas');
				var temp_ctx = temp_canvas.getContext('2d');
				renderPage(i,temp_canvas,temp_ctx,false)
				$(temp_canvas).addClass('jump_page');
				$(temp_canvas).attr('page_number',i);
				$(temp_canvas).css('width','100%');
				$(temp_canvas).css('float','left');
				$(temp_canvas).css('padding','10%');
				$('div#pdf_preview_modal .modal-body .page_datas').append(temp_canvas)
				
				
				i+=1
				
			}
			
			$('canvas.jump_page').click(function(){
				var p_num = $(this).attr('page_number');
				pageNum = parseInt(p_num)
				queueRenderPage(parseInt(p_num));
			})
		}
		
		function renderPage(num,canv,cur_ctx,main_preview) {
			  pageRendering = true;
			  // Using promise to fetch the page
			  pdfDoc.getPage(num).then(function(page) {
			    var viewport = page.getViewport({scale: scale,rotation:rotation});
			    canv.height = viewport.height;
			    canv.width = viewport.width;
			
			    // Render PDF page into canvas context
    			var renderContext = {
    			  canvasContext: cur_ctx,
    			  viewport: viewport
    			};
    			var renderTask = page.render(renderContext);
    			
			
    			// Wait for rendering to finish
	    			renderTask.promise.then(function() {
	    			  pageRendering = false;
	    			  if (pageNumPending !== null) {
	    			    // New page rendering is pending
	    			    renderPage(pageNumPending,canv);
	    			    pageNumPending = null;
	    			  }
	    			});
			  });
			  if(main_preview) {
				  document.getElementById('page_num').value = num; 
				  $('canvas.jump_page').removeClass('page_highlight')
				  $("canvas[page_number='" + pageNum.toString() + "']").addClass('page_highlight');
			  }
			  
		}
		
		function queueRenderPage(num) {
			  if (pageRendering) {
			    pageNumPending = num;
			  } else {
			    renderPage(num,canvas,ctx,true);
			  }
		}
		
		/**
		 * Displays previous page.
		 */
		function onPrevPage() {
		  if (pageNum <= 1) {
		    return;
		  }
		  pageNum--;
		  queueRenderPage(pageNum);
		}
			
			
		function onNextPage() {
		  if (pageNum >= pdfDoc.numPages) {
		    return;
		  }
		  pageNum++;
		  queueRenderPage(pageNum);
		}
		
		function onZoomIn() {
			if(scale <= 10) {
				$('#pdf_preview_modal #zoomin').prop('disabled',false)
				$('#pdf_preview_modal #zoomin').css('color','black')
				$('#pdf_preview_modal #zoomout').css('color','black')
				scale += 0.25;
				renderPage(pageNum,canvas,ctx,true);
			}
			else {
				$('#pdf_preview_modal #zoomin').prop('disabled',true)
				$('#pdf_preview_modal #zoomin').css('color','grey')
				$('#pdf_preview_modal #zoomout').css('color','black')
			}
		}
		
		function onZoomOut() {
			if(scale > 0.25) {
				$('#pdf_preview_modal #zoomout').prop('disabled',false)
				$('#pdf_preview_modal #zoomout').css('color','black')
				$('#pdf_preview_modal #zoomin').css('color','black')
			  scale -= 0.25;
			  renderPage(pageNum,canvas,ctx,true);
			}
			else {
				$('#pdf_preview_modal #zoomout').prop('disabled',true)
				$('#pdf_preview_modal #zoomout').css('color','grey')
				$('#pdf_preview_modal #zoomin').css('color','black')
			}
		}
		
		function onClockWWise() {
			if (rotation == 0){
				rotation = 90;
				renderPage(pageNum,canvas,ctx,true);
			}
			else if (rotation == 90){
				rotation = 180;
				renderPage(pageNum,canvas,ctx,true);
			}
			else if (rotation == 180){
				rotation = 270;
				renderPage(pageNum,canvas,ctx,true);
			}
			else if (rotation == 270){
				rotation = 0;
				renderPage(pageNum,canvas,ctx,true);
			}
		}
		
		function onAntiClockwise() {
			if (rotation == 0){
				rotation = 270;
				renderPage(pageNum,canvas,ctx,true);
			}
			else if (rotation == 90){
				rotation = 0;
				renderPage(pageNum,canvas,ctx,true);
			}
			else if (rotation == 180){
				rotation = 90;
				renderPage(pageNum,canvas,ctx,true);
			}
			else if (rotation == 270){
				rotation = 180;
				renderPage(pageNum,canvas,ctx,true);
			}
			
		}
		
		
		function render_pdf_preview(base64_data,url) {
				// Loaded via <script> tag, create shortcut to access PDF.js exports.
        		var pdfjsLib = window['pdfjs-dist/build/pdf'];

        		// The workerSrc property shall be specified.
//        		pdfjsLib.GlobalWorkerOptions.workerSrc = '//mozilla.github.io/pdf.js/build/pdf.worker.js';
        		
        		pdfjsLib.GlobalWorkerOptions.workerSrc = '/website_pdf_preview/static/src/js/pdf.worker.js';
        		
      			document.getElementById('prev').addEventListener('click', onPrevPage);
      			
      			document.getElementById('next').addEventListener('click', onNextPage);
      			
      			document.getElementById('zoomin').addEventListener('click', onZoomIn);
      			
      			document.getElementById('zoomout').addEventListener('click', onZoomOut);
      			
      			document.getElementById('clockwise').addEventListener('click', onClockWWise);
      			
      			document.getElementById('anti-clockwise').addEventListener('click', onAntiClockwise);
      			
      			
      			$("#page_num").keydown(function (e) {
      			  if (e.keyCode == 13) {
      				  if(parseInt($(this).val()) <= pdfDoc.numPages) {
      					  pageNum = parseInt($(this).val())
      					  renderPage(parseInt($(this).val()),canvas,ctx,true);
      				  }
      				  else
      					$(this).val(pageNum) 
      			  }
      			});
	
      			var loadingTask = false;
      			
        		if(base64_data) {
        			loadingTask = pdfjsLib.getDocument({data: base64_data});
        		}
        		
        		if (url) {
        			loadingTask = pdfjsLib.getDocument(url);
        		}
        		
        		loadingTask.promise.then(function(pdf) {
        			  pdfDoc = pdf;
        			  document.getElementById('page_count').textContent = pdfDoc.numPages;
        			  renderPage(pageNum,canvas,ctx,true);
        			  renderAllPage();
        			  $('canvas.jump_page').removeClass('page_highlight')
    				  $("canvas[page_number='" + pageNum.toString() + "']").addClass('page_highlight');
        			}, function (reason) {
        			  // PDF loading error
        			  console.error(reason);
    			});
        		
        		$('div#pdf_preview_modal').modal('show');
        		$("div#pdf_preview_modal").data('bs.modal')._config.backdrop = 'static'; 
        		
        		var modal_height = ($('#pdf_preview_modal')[0].offsetHeight  - $('#pdf_preview_modal .modal-header')[0].offsetHeight - $('#pdf_preview_modal .modal-header')[0].offsetHeight).toString() + 'px';
	   		    var modal_width = $('#pdf_preview_modal').width().toString() + 'px';
	   		    $('#pdf_preview_modal .modal-body').css('height',modal_height)
	   		    $('#pdf_preview_modal .page_datas').css('height',modal_height)
	   		    $('#pdf_preview_modal #main_handler').css('height',modal_height)
	   		    
	   		    $('#pdf_preview_modal .modal-body').css('width',modal_width)
	   		    $('#pdf_preview_modal .page_datas').css('width',modal_width)
	   		    $('#pdf_preview_modal #main_handler').css('width',modal_width)
	   		    
	   		    
        		$.getScript("/website_pdf_preview/static/src/js/dragscroll.js",function(){
    				console.log("")
				});
			}
		
		$('a.pdf_preview').click(function(ev){
			ev.preventDefault();
			var d_href = $(this).attr('href')
			var self = this;
			ajax.jsonRpc('/pdf_preview_modal', 'call', {'href' : $(this).attr('href')})
			.then(function(attachment_data){
            		if(attachment_data) {
						var download_href=false
	            		if(attachment_data['type'] == 'binary') {
	            			download_href = $(self).attr('href')
	            		}
	            		else {
	            			download_href = "data:application/pdf;base64,"
	    					download_href += attachment_data['base64_data']
	            		}
	            		var html =
	            			      '<div class="modal" id="pdf_preview_modal" tabindex="-1" role="dialog">'+
	            			          '<div class="modal-dialog modal-dialog-centered" role="document" data-backdrop="static" data-keyboard="false" style="max-width:100%;">'+
	            			              '<div class="modal-content">'+
				        					  '<div class="modal-header row" style="margin:0;">' +
				            			        '<div class="col-4">'+
		            			        			'<span class="fa fa-plus pdf-icons" id="zoomin" style="font-size:1vw;border-radius: 50%;padding: 8px 16px;"></span>'+
													'<span class="fa fa-minus pdf-icons" id="zoomout" style="font-size:1vw;border-radius: 50%;padding: 8px 16px;"></span>'+
													'<span class="fa fa-rotate-right pdf-icons" id="clockwise" style="font-size:1vw;border-radius: 50%;padding: 8px 16px;"></span>'+
													'<span class="fa fa-rotate-left pdf-icons" id="anti-clockwise" style="font-size:1vw;border-radius: 50%;padding: 8px 16px;"></span>'+
				            			        '</div>'+
				            			        '<div class="col-4" style="text-align:center;">'+
												    '<span class="fa fa-chevron-circle-left pdf-icons pdf-icons-nav" id="prev" style="font-size:1vw;border-radius: 50%;padding: 8px 16px;"></span>'+
												    '<span style="font-size:1vw;" class="pdf-icons">Page: <input type="text" id="page_num" style="width:8%;"></input> / <span id="page_count"></span></span>'+
												    '<span class="fa fa-chevron-circle-right pdf-icons pdf-icons-nav" id="next" style="font-size:1vw;border-radius: 50%;padding: 8px 16px;"></span>'+
												'</div>'+
												'<div class="col-4" style="text-align:center;">'+
												  '<a class="fa fa-download pdf-icons pdf_download" href="' + download_href + '" download="' + attachment_data['filename'] + '" style="color:black;font-size:1vw;border-radius: 50%;padding: 8px 16px;"/>'+
												  '<button type="button" class="pdf_preview_close close" data-dismiss="modal" aria-label="Close">' +
				            			             '<span>×</span>' +
				            			          '</button>' +
											    '</div>'+
				            			      '</div>' +
				            			      '<div class="modal-body row" style="overflow:hidden;">' +
				            			      	'<div class="page_datas col-2" style="overflow:scroll;background-color:black;"> </div>'+
				            			        '<div class="col-10 dragscroll" id="main_handler" style="overflow:scroll;cursor: grab; cursor : -o-grab; cursor : -moz-grab; cursor : -webkit-grab;">'+
				            			      		'<canvas id="pdf-preview-canvas"></canvas>' +
				            			        '</div>'+
				            			        '<div id="text-layer"></div>'+
				            			      '</div>' +
								   		  '</div>'+
							   		  '</div>'+
						   		  '</div>';
	
	            		
				   		if(attachment_data['type'] == 'binary' && attachment_data['mimetype'] == 'application/pdf') {
				   		    $('body').append(html);
				   		    
				   		    canvas = document.getElementById('pdf-preview-canvas'),
			   			    ctx = canvas.getContext('2d');
				   		    
				   		    if(!attachment_data['public_pdf'] && attachment_data['public_user']) {
				   		    	$('#pdf_preview_modal .pdf_download').hide()
				   		    }
				   		    
		            		$('button.pdf_preview_close').click(function(e){
		            			e.preventDefault();
		            			$('div#pdf_preview_modal').modal('hide');
		            			$('div#pdf_preview_modal').remove();
		            			pdfDoc = null;
		    				    pageNum = 1;
		    				    pageRendering = false;
		    				    pageNumPending = null;
		    				    scale = 1.0;
		    				    rotation = 0;
		    					canvas = false;
		    				    ctx = false;
		            		})
		            		
		            		var pdfData = atob(attachment_data['base64_data'])
		    				render_pdf_preview(pdfData,false)
				   		}
				   		else if(attachment_data['type'] == 'url' && attachment_data['mimetype'] == 'application/pdf') {
			   				$('body').append(html);
			   				
			   				canvas = document.getElementById('pdf-preview-canvas'),
			   			    ctx = canvas.getContext('2d');
			   				
			   				if(!attachment_data['public_pdf'] && attachment_data['public_user']) {
				   		    	$('#pdf_preview_modal .pdf_download').hide()
				   		    }
			   				
		            		$('button.pdf_preview_close').click(function(e){
		            			e.preventDefault();
		            			$('div#pdf_preview_modal').modal('hide');
		            			$('div#pdf_preview_modal').remove();
		            			pdfDoc = null;
		    				    pageNum = 1;
		    				    pageRendering = false;
		    				    pageNumPending = null;
		    				    scale = 1.0;
		    				    rotation = 0;
		    					canvas = false;
		    				    ctx = false;
		            		})
		            		var pdfurl = attachment_data['url']
		    				render_pdf_preview(false,pdfurl)
				   		}
            		}
            		else {
            			window.location = d_href;
            		}
            })
		})
	})

})