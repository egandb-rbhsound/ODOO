odoo.define('dealer.backend.dashboard',function (require) {
	'use strict'

	/* Copyright (c) 2018-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>) */
	/* See LICENSE file for full copyright and licensing details. */

  var AbstractAction = require('web.AbstractAction');
	var core = require('web.core');
  var ajax = require('web.ajax');
  var ConfigMixin = require('dealership.config.mixin');
  var _t = core._t;
	var IsLoadedJS = true;

  var data = {
      labels: ['Red', 'Blue', 'Yellow', 'Green', 'Purple', 'Orange'],
      datasets: [{
          label: '# of Votes',
          data: [12, 19, 3, 5, 2, 3],
          backgroundColor: '#5C9BEF',
          borderColor: '#5C9BEF',
          borderWidth: 1
      }]
  };

  var options = {
    legend: {
      display: false
    }
  };

  var scales = {
    xAxes: [{
        gridLines: {
          drawOnChartArea: false,
        },
        ticks: {
          beginAtZero: true
        }
    }],
    yAxes: [{
        gridLines: {
          drawOnChartArea: false,
        },
        ticks: {
          beginAtZero: true
        }
    }]
  };


  var text = _t('REGISTRATION')
  var centerText = {
		center: {
			text: text,
		}
	};

  var Dashboard = AbstractAction.extend( ConfigMixin, {
    template: 'dealer_backend_dashboard',

    jsLibs: ['/web/static/lib/Chart/Chart.js'],

    events: {
      'click .change-chart': '_changeChartType',
      'click .toggle-chart': '_changeChartData',
      'click .card-header .dropdown-item': '_updateChartData',
      'click .card-body .dropdown-item': '_updateMapData',
			'change .dropdown-toggle': '_getUpdatedChartData',
      'click .view-leads': '_getLeadsPage',
			'click .top_tags .con': '_openRecords'
    },



    _loadDashBoard: function () {
      var self = this;
      return  self._rpc({
          route: '/dashboard/home',
          params: {}
        }).then(function (resposne) {
          self.dataset = resposne;
        })
    },

    _loadData: function (params) {
      return this._rpc({
        route: '/dashboard/update_data',
        params: params
      })
    },

    willStart: function () {
      var proms = [this._loadDashBoard(), this._super()];
      return Promise.all(proms);;
    },

    start: function () {
      var self = this;
      this._super().then(function () {
        self._chartRegistry();
        self.chartTopLeads();
        self.chartTopProducts();
        self.chartDealerRegistration();
        self.chartPlanFilter();
        self.chartContractState();
        self.chartSaleState();
      });
			self._initDealer();
    },

    chartTopLeads: function () {
			var max = Math.max(...this.dataset.total_leads_stat.datasets[0].data) + 5;
      var $ele = this.$el.find('#ctx_top_leads');
      var l_option = {
        responsive: true,
        scales: {
          yAxes: [{
              barPercentage: .3,
              categoryPercentage: 1,
              gridLines: {
                  display: false,
                  drawBorder: false
              },
							ticks: {
	                beginAtZero: true
	            }
          }],
					xAxes: [{
						display: false,
						ticks: {
								beginAtZero: true,
								max: max
						},
						gridLines: {
								display: false,
								drawBorder: false
						},
					}]
        },
        legend: {
          display: false
        }
      };


      var myChart = new Chart($ele, {
          type: 'horizontalBar',
          data: this.dataset.total_leads_stat,
          options: l_option
      });
    },

    chartTopProducts: function () {
      var $ele = this.$el.find('#ctx_top_products');
      this.ctx_top_products = this._renderChart($ele, 'bar', this.dataset.top_products_stat, options);
    },

    chartDealerRegistration: function () {
      var $ele = this.$el.find('#ctx_registration');
      this.ctx_registration = this._renderChart($ele, 'doughnut', this.dataset.total_registration_stat, options);
    },

    chartPlanFilter: function () {
      var $ele = this.$el.find('#ctx_plan_filter');
      this.ctx_plan_filter = this._renderChart($ele, 'doughnut', this.dataset.plan_stat, options);
    },

    chartContractState: function () {
      var $ele = this.$el.find('#ctx_contract_state');

      this.ctx_contract_state = this._renderChart($ele, 'doughnut', this.dataset.contract_state, options);
    },

    chartSaleState: function () {
      var $ele = this.$el.find('#ctx_sales_state');
      this.ctx_sales_state = this._renderChart($ele, 'doughnut', this.dataset.total_sale_stat, options);
    },

    _chartRegistry: function () {
      Chart.pluginService.register({
        beforeDraw: function (chart) {
					// use to add center text in doughnut chart
          if (chart.config.options.elements.center) {
            var ctx = chart.chart.ctx;
            var centerConfig = chart.config.options.elements.center;
            var txt = centerConfig.text;
            var color = centerConfig.color || '#000';
            var sidePadding = centerConfig.sidePadding || 30;
            var sidePaddingCalculated = (sidePadding/100) * (chart.innerRadius * 2)
            ctx.font = "bold 30px Arial"; //+ fontStyle;
            var stringWidth = ctx.measureText(txt).width;
            var elementWidth = (chart.innerRadius * 2) - sidePaddingCalculated;
            var widthRatio = elementWidth / stringWidth;
            var newFontSize = Math.floor(30 * widthRatio);
            var elementHeight = (chart.innerRadius * 2);
            var fontSizeToUse = Math.min(newFontSize, elementHeight);
            ctx.textAlign = 'center';
            ctx.textBaseline = 'middle';
            var centerX = ((chart.chartArea.left + chart.chartArea.right) / 2);
            var centerY = ((chart.chartArea.top + chart.chartArea.bottom) / 2);
            ctx.font = "bold "+fontSizeToUse+"px Arial" //+ fontStyle;
            ctx.fillStyle = color;
            ctx.fillText(txt, centerX, centerY);
          }
        },

				afterDatasetsDraw: function(chart, easing) {
					// use to lable right of the bar
					 var ctx = chart.ctx;
					 if (ctx.canvas.getAttribute('id') == 'ctx_top_leads') {
						 chart.data.datasets.forEach(function (dataset, i) {
								 var meta = chart.getDatasetMeta(i);
								 if (!meta.hidden) {
										 meta.data.forEach(function(element, index) {
												 ctx.fillStyle = '#A7A7A7';
												 var fontSize = 16;
												 var fontStyle = 'normal';
												 var fontFamily = 'Lucida Grande';
												 ctx.font = Chart.helpers.fontString(fontSize, fontStyle, fontFamily);
												 var dataString = dataset.data[index].toString();
												 ctx.textAlign = 'center';
												 ctx.textBaseline = 'middle';
												 var padding = 5;
												 var position = element.tooltipPosition();
												 ctx.fillText(dataString, position.x+15, (position.y+15) - (fontSize / 2) - padding);
										 });
									 }
							 });
						 }
					 }
      });
    },

    _changeChartType: function (ev) {
      try {
        var dataset = ev.currentTarget.dataset;
        var selector = dataset.value;
        var type = dataset.type;
        var data = this.dataset[dataset.load];
        var $ele = this.$el.find(`#${selector}`);
        var $button = $ele.closest('.card').find('.dropdown-toggle');

        if ($button.length > 0) {
          $button.attr('data-chart', type);
        }

        this[selector].destroy();
        var new_chart = this._renderChart($ele, type, data, options);
        this[selector] = new_chart;
      } catch (e) {
        console.log(e);
      }
    },

    _changeChartData: function (ev) {
      var self = this;
      var $el = $(ev.currentTarget);
      var selector = ev.currentTarget.dataset.value;
      var type = ev.currentTarget.dataset.type;
      var $ele = this.$el.find(`#${selector}`);
      var $card = $el.closest('.card');

      $el.closest('.btn-group').find('button').removeClass('active');
      $el.addClass('active');
      $card.find('canvas').addClass('d-none');
      $ele.removeClass('d-none');

      var call = $el.data('call');
      $card.find('.dropdown-toggle').each(function() {
        this.dataset.call = call;
        this.dataset.selector = selector
      })

      if (self.hasOwnProperty(selector)) {
        self[selector].destroy();
      }

      $card.find('.dropdown-toggle').first().trigger('change');
    },

    _updateChartData: function (ev) {
      ev.preventDefault();
      var value = ev.currentTarget.dataset.value;
      var text = ev.currentTarget.innerHTML;
      var $button = $(ev.currentTarget).closest('.btn-group').find('.dropdown-toggle');
      $button.html(text);
      $button.attr('data-value', value);
      $button.trigger('change');
    },

    _getUpdatedChartData: function (ev) {
      var self = this;
      var ele = ev.currentTarget;
      var $card = $(ele).closest('.card').find('.card-header');
      var selector = ev.currentTarget.dataset.selector;
      var type = ev.currentTarget.dataset.chart;
      var params = {'call': ele.dataset.call};
      var $ele = this.$el.find(`#${selector}`);

      $card.find('.dropdown-toggle').each(function () {
        params[this.dataset.type] = parseInt(this.dataset.value);
      })

      self._loadData(params).then(function (response) {
        if (response) {
          if (self[selector]) {
            self[selector].destroy();
          }
          var new_chart = self._renderChart($ele, type, response, options);
          self[selector] = new_chart;
          self.dataset[params.call] = response;
        }
      });
    },

    colorLighter: function(color, percent) {
      	var num = parseInt(color.replace('#', ''),16),
    		amt = Math.round(2.55 * percent),
    		R = (num >> 16) + amt,
    		B = (num >> 8 & 0x00FF) + amt,
    		G = (num & 0x0000FF) + amt;
        var color = (0x1000000 + (R<255?R<1?0:R:255)*0x10000 + (B<255?B<1?0:B:255)*0x100 + (G<255?G<1?0:G:255)).toString(16).slice(1);
    		return "#"+color;
    },

    _renderChart: function (ctx, type, data, option) {
      var x_option = {};
      Object.assign(x_option, option);

      if (type != 'doughnut') {
        x_option['scales'] = scales;
      } else {
        try {
          var length = data.datasets[0].data.length;
          var color = data.datasets[0].backgroundColor;
          if (typeof color == 'string') {

            var update_color = [color];
            for (let i=0; i < length; i++) {
              color = this.colorLighter(color, 5);
              update_color.push(color);
            }
						data.datasets[0].backgroundColor = update_color;
            data.datasets[0].hoverBackgroundColor = update_color;
						data.datasets[0].borderColor = update_color;
            data.datasets[0].hoverBorderColor = update_color;
          }
        } catch (e) {}

        if (ctx.attr('id') == 'ctx_registration') {
          x_option.elements = centerText;
					x_option['cutoutPercentage'] = 75;
        }
      }

			x_option.legend.display = false;
			if (data.legend_text) {
				ctx.parent().find('.legend').remove();
				var html = "<div class='w-100 legend row mt-4'>";
				data.legend_text.forEach(function (item, index) {
					var color = data.datasets[0].backgroundColor;
					if (typeof color != 'string') {
						color = color[index];
					}
					html += `<div class="col-6 mt-2 mb-2 text-dark"><strong><i class="fa fa-circle mr-2" style="color: ${color}"/>${item}</strong></div>`;
				})
				html += "</div>";
				ctx.after(html);
			}
      var myChart = new Chart(ctx, {
          type: type,
          data: data,
          options: x_option
      });
      return myChart;
    },


    _initDealer: function () {
      var self = this;
      if (this.dataset.location.map_key.length > 0 && IsLoadedJS) {
        var api = `https://maps.googleapis.com/maps/api/js?key=${this.dataset.location.map_key}&amp;libraries=places`;
        $.getScript(api, function() {
            self.dataset.location.map_api = true;
						IsLoadedJS = false;
            self._getDealer();
        });
      } else if (!typeof google === 'undefined') {
				self.dataset.location.map_api = true;
				self._getDealer();
			}
    },



    _getDealer: function () {
      var self = this;
      var map_ele = self.el.querySelector('#g_map');
      var $card = $(map_ele).closest(".card-body");
      $card.find('.alert').addClass('d-none');

      if (this.dataset.location.map_api) {
        var params = {
          'call': 'dealer_location_stat'
        }


        if (this.dataset.location.current_state) {
          params.state_id = parseInt(this.dataset.location.current_state);
        }
        if (this.dataset.location.current_country) {
          params.country_id = parseInt(this.dataset.location.current_country);
        }

        self._loadData(params).then(function(response) {
          if (response.applications ) {
            map_ele.style.height = "400px";

            self.map = new google.maps.Map(map_ele, {
              zoom: 4,
              center: {lat: 0.0, lng: 0.0},
              mapTypeId: google.maps.MapTypeId.ROADMAP
            });

            self.Geocoder = new google.maps.Geocoder();
            self.bounds = new google.maps.LatLngBounds();

            response = self._parseResponse(response);
            self._createMarkers(response);
          } else {
            $card.find('.not-found').removeClass('d-none');
          }
        });
      } else  {
        $card.find('.api_missing').removeClass('d-none');
      }

    },

    _updateMapData: function(ev) {
      ev.preventDefault();
      var self = this;
      var ele = ev.currentTarget;
      var value = parseInt(ele.dataset.value);
      var el = ele.innerHTML;
      var $state = this.$el.find('#state');
      $(ele).closest('.btn-group').find('.dropdown-toggle').html(el);

      if (ele.classList.contains('country')) {
        this.dataset.location.current_country = value;
        this.dataset.location.current_state = false;
        $state.html(_t('State'));
        var url = `/shop/country_infos/${value}`;
        ajax.jsonRpc(url, 'call', { "mode": "" }).then(function (response) {
          var dropDown = $state.closest('.btn-group').find('.dropdown-menu');
          dropDown.empty();
          if (response) {
            var state = response.states;
            var $option = "";
            state.forEach(function (item) {
              $option += `<a class="dropdown-item" data-value="${item[0]}" href="#" >${item[1]}</a>`;
            })
            dropDown.html($option);
          }
        })
      } else {
        this.dataset.location.current_state = value;
      }
      self._getDealer();
    },

    _parseResponse: function(response) {
      var data = [];
      response.applications.forEach(function (item) {
        var dict = {};
        dict.count = String(item[item.length - 1]);
        item.splice(-1,1);
        dict.full_address = response.name + ' ' + item.join(" ");
        data.push(dict);
      })
      return {'applications': data};
    },

    _addMarker: function (config) {
      var self = this;
      var marker = new google.maps.Marker({
        position: config.coords,
        map: this.map,
      });

      var infoWindow = new google.maps.InfoWindow({
        content: 'Dealers ' + config.count
      });

      marker.addListener('click', function () {
        if (self.activeWindow) {
          self.activeWindow.close();
        }
        infoWindow.open(self.map, marker);
        self.activeWindow = infoWindow;
      });

      self.bounds.extend(marker.position);
      self.map.fitBounds(self.bounds);
    },

		_getLeadsPage: function (ev) {
			ev.preventDefault();
			var domain = ['user_id', '!=', false];

			if (ev.currentTarget.dataset.assigned) {
				domain = ['user_id', '=', false];
			}

			domain = [domain];

			this.do_action({
				type: 'ir.actions.act_window',
				name: _t('Leads'),
				res_model: 'crm.lead',
				views: [[false, 'tree']],
				view_mode: 'list',
				domain: domain
			});
		},

		_openRecords: function (ev) {
			var action = JSON.parse($(ev.currentTarget).attr('action'));
			this.do_action({
				type: 'ir.actions.act_window',
				views: action.views,
				name: action.name,
				res_model: action.model,
        search_view_id: [false],
				domain: action.domain
			});
		}


  })


  core.action_registry.add('dealer_backend_dashboard', Dashboard);
});
