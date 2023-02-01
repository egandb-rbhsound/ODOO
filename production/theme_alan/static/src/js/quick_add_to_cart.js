odoo.define('theme_alan.quick_add_to_cart', function (require) {
"use strict";

var publicWidget = require('web.public.widget');
var varientMixin = require('sale.VariantMixin');


publicWidget.registry.quickAddToCart = publicWidget.Widget.extend({
    selector: '#wrapwrap',
    events : {
        "click a.js_quick_cart": "_quickAddToCart",
        "click a.ajax_add_cart": "_ajaxAddToCart",
        "click a.ajax_cart_no_varient": "_ajaxAddCartNoVerient"
    },
    _quickCart:function(self,prod_varient_id,product_temp_id,formVals,customVals,varient){
        return self._rpc({
            route: '/quick_update_cart',
            params: {
                'prod_varient_id':prod_varient_id,
                'product_temp_id':product_temp_id,
                'varient':varient,
                'formVals':formVals,
                'customVals': customVals
            }
        }).then(function (result) {
            var preCartQty = self.$target.find('.my_cart_quantity').html();
            if(preCartQty.trim() != ''){
                var currCartQty = parseInt(preCartQty) + result['add_qty'];
                self.$target.find('.my_cart_quantity').html(currCartQty);
            }else{
                self.$target.find('.my_cart_quantity').html(result['add_qty']);
            }
            return self._rpc({
                route: '/quick_suggestion_and_notifier',
                params: {
                    'prod_id':result['prod_temp_id']
                }
            }).then(function (result) {
                self.$target.find('.quick_cart_base').empty().append(result['template']);
                self.$target.find('#quick_cart_detail_modal').modal('show');
                $('.as_confirm_product_slider').owlCarousel({
                    loop: true,
                    rewind: true,
                    margin: 10,
                    nav: true,
                    lazyLoad:true,
                    dots: false,
                    navText : ['<span aria-label="Previous"></span>', '<span aria-label="Next"></span>'],
                    items: 2,
                });
            });

        });

    },
    _ajaxAddCartNoVerient:function(ev){
        var self = this;
        var prod_varient_id = $(ev.currentTarget).data('product_varient_id');
        var prod_temp_id = $(ev.currentTarget).data('product_template_id');
        this._quickCart(self,prod_varient_id,prod_temp_id,[],[],false);
    },
    _ajaxAddToCart:function(ev){
        var self = this;
        var $getForm = $(ev.currentTarget).parents('form');
        var formVals = $getForm.serializeArray();
        var customVals = varientMixin.getCustomVariantValues($getForm);
        this._quickCart(self,0,0,formVals,customVals,true);
    },
    _quickAddToCart:function(ev){
        var self = this;
        var prodId = $(ev.currentTarget).data('product-id')
        return this._rpc({
            route: '/get/quick_add_to_cart',
            params: {
                'prodId':prodId
            }
        }).then(function (result) {
            console.log(result);
            self.$target.find('.quick_cart_base').empty().append(result['template']);
            self.$target.find('#quick_cart_modal').modal('show');

            var sale = new publicWidget.registry.WebsiteSale();
            sale.init();
            $("[data-attribute_exclusions]").on("change", function(event) {
                sale.onChangeVariant(event);
            });
            $("[data-attribute_exclusions]").trigger("change");
            $(".css_attribute_color input").click(function(event){
                sale._changeColorAttribute(event);
            });
            // Add to cart from Quick View
            $(".a-submit").on("click", function(event) {
                sale._onClickAdd(event);
            });
            $('#buy_now').on('click', function(event){
                sale._onClickAdd(event);
            })
            // Add Quantity from Quick View
            $("a.js_add_cart_json").on("click", function(event) {
                sale._onClickAddCartJSON(event);
            });
            // Change Quantity from Quick View
            $("input[name='add_qty']").on("change", function(event) {
                sale._onChangeAddQuantity(event);
            });

        });
    }
});
});
