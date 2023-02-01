odoo.define('dealership.management.faq', function (require) {
  'use strict';

  /* Copyright (c) 2018-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>) */
  /* See LICENSE file for full copyright and licensing details. */

  var publicWidget = require('web.public.widget');
  var core = require('web.core');
  var _t = core._t;

  publicWidget.registry.websiteDealerFAQ = publicWidget.Widget.extend({
    xmlDependencies: ['/dealership_management/static/src/xml/faq_template.xml'],
    selector: '.dealer-faqs',
    events: {
      'click .category button': '_callAllLines',
      'click .read-more': '_callSingleFaq',
      'click #get_back_faq': '_getBackFAQ',
      'click .search-faq-items button': '_searchFAQItems'
    },

    start: function () {
      var id = parseInt(this.$target.find('#accordion').attr('data_id'), 10);
      this.params = {'faq_category': id};
      this.back = $("#get_back_faq");
      var self = this;
      self._callBack = function (resposne) {
        self.back.addClass('d-none');
        $('#dealer_faq_item').remove();
        var html = $(core.qweb.render('dealership_management.dealer_faq_items', resposne));
        self.$target.find('#accordion').html(html);
        $("#head").text(resposne.head);
        $("#item_description").text(resposne.description);
        $('.category button').removeClass('active');
        $(`.category #${self.params.faq_category}`).addClass('active');
      };
      this._getFAQLines(self._callBack);
    },

    _callAllLines: function (ev) {
      var id = parseInt(ev.currentTarget.getAttribute("id"), 10);
      this.params.faq_category = id;
      this._getFAQLines(this._callBack);
    },

    _callSingleFaq: function (ev) {
      ev.preventDefault();
      var self = this;
      var id = parseInt(ev.currentTarget.getAttribute("id"), 10);
      this.params.faq = id;
      var $ele = this.$target.find('#accordion');
      var _callBack = function functionName(resposne) {
        $ele.find('.card').hide('fast');
        self.back.removeClass('d-none');
        $ele.append($(core.qweb.render('dealership_management.dealer_faq_item', resposne)));
      };

      this._getFAQLines(_callBack);
    },

    _getBackFAQ: function (ev) {
      ev.preventDefault();
      var $ele = this.$target.find('#accordion');
      $('#dealer_faq_item').remove();
      $ele.find('.card').show('fast');
      this.back.addClass('d-none');
    },

    _searchFAQItems: function (ev) {
      var search = this.$target.find('.search-faq-items input').val();
      if ( search.length > 1 ) {
        this.params.search = search;
        this._getFAQLines(this._callBack);
      }
    },


    _getFAQLines: function (_callBack) {
      var self = this;
      self._rpc({
        route: '/dealer/faq_items',
        params: self.params
      }).then(function (resposne) {
        _callBack(resposne);
        self.params = {};
      })
    }


  });


});
