$(function(){
    var Event = Backbone.Model.extend({
        idAttribute: "resource_uri",
        url: function() {
            return this.get('resource_uri') || this.collection.url;
        }
    });

    var Events = Backbone.Collection.extend({
        model: Event,
        url: SHIFTS_API,
        parse: function(data) {
            return data.objects;
        }
    });

    var User = Backbone.Model.extend({
        idAttribute: "resource_uri",
        url: function() {
            return this.get('resource_uri') || this.collection.url;
        }
    });

    var Users = Backbone.Collection.extend({
        model: User,
        url: USERS_API,
        parse: function(data) {
            return data.objects;
        }
    });

    var EventsView = Backbone.View.extend({
        initialize: function(){
            _.bindAll(this);

            this.collection.bind('reset', this.addAll);
            this.collection.bind('add', this.addOne);
            this.collection.bind('change', this.change);
            this.collection.bind('destroy', this.destroy);

            this.eventView = new EventView();
        },
        render: function() {
            this.el.fullCalendar({
                header: {
                    left: 'prev,next today',
                    center: 'title',
                    right: '',
                    ignoreTimezone: false
                },
                selectable: true,
                selectHelper: true,
                editable: true,
                select: this.select,
                eventClick: this.eventClick,
                eventDrop: this.eventDropOrResize,
                eventResize: this.eventDropOrResize,
                events: 'events',
                defaultView: 'agendaWeek',
                firstHour: 8,
                allDaySlot: false
            });
        },
        addAll: function(){
//            var test = this.collection.toJSON();
            this.el.fullCalendar('addEventSource', this.collection.toJSON());
        },
        addOne: function(event) {
            this.el.fullCalendar('renderEvent', event.toJSON(), true);
        },
        select: function(start, end, allDay) {
            this.eventView.collection = this.collection;
            this.eventView.model = new Event({start: start, end: end, allDay: allDay});
            this.eventView.render();
        },
        eventClick: function(fcEvent) {
            this.eventView.model = this.collection.get(fcEvent.resource_uri);
            this.eventView.render();
        },
        change: function(event) {
            var fcEvent = this.el.fullCalendar('clientEvents', event.get('id'))[0];
            fcEvent.title = event.get('title');
            fcEvent.for_trade = event.get('for_trade');
            fcEvent.color = event.get('color');
            this.el.fullCalendar('updateEvent', fcEvent);
        },
        eventDropOrResize: function(fcEvent) {
            this.collection.get(fcEvent.resource_uri).save({start: fcEvent.start, end: fcEvent.end});
        },
        destroy: function(event) {
            this.el.fullCalendar('removeEvents', event.get('id'));
        }
    });

    var EventView = Backbone.View.extend({
        el: $("#eventDialog"),
        initialize: function() {
            _.bindAll(this);
        },
        render: function() {
            var buttons = {};
            _.extend(buttons, {'Save': this.save});
            if (this.model.get('for_trade')) {
                _.extend(buttons, {'Take Shift': this.take_shift});
            } else if (this.model.get('title') == 
                       Backbone.Tastypie.apiKey.username) {
                _.extend(buttons, {'Trade Shift': this.trade_shift});
            }
            if (!this.model.isNew()) {
                _.extend(buttons, {'Delete': this.destroy});
            }

            this.el.dialog({
                modal: true,
                title: (this.model.isNew() ? 'New' : 'Edit') + ' Shift',
                buttons: buttons,
                open: this.open,
            });

            return this;
        },
        open: function() {
            this.$("#conWorking option[value=" + this.model.get("title") +"]").attr("selected", "selected");
            
        },
        save: function() {
            this.model.set({'title': this.$("#conWorking").val(),
			    'loc': this.$("#loc").val()});
            
            if (this.model.isNew()) {
                this.collection.create(this.model, {success: this.close});
            } else {
                this.model.save({}, {success: this.close});
            }
        },
        take_shift: function() {
            this.model.set({'for_trade': false, 'color': 'Blue',
                            'title': Backbone.Tastypie.apiKey.username});
            this.model.save({}, {success: this.close});
        },
        // it would be nice to not have this as a separate function, but
        // this is the easy way for now
        trade_shift: function() {
            this.model.set({'for_trade': true, 'color': 'Red'});
            this.model.save({}, {success: this.close});
        },
        close: function() {
            this.el.dialog('close');
        },
        destroy: function() {
            this.model.destroy({success: this.close});
        }
    });
    
    var events = new Events();
    new EventsView({el: $("#calendar"), collection: events}).render();
    events.fetch();

    var users = new Users();
    // on success, populate the #conWorking dropdown list with users
    users.fetch({success: function(model, response) {
        model.each(function (u) {
            $("#conWorking")
                .append($('<option></option>')
                        .val(u.get('username'))
                        .html(u.get('first_name') + 
                              ' ' +  
                              u.get('last_name')));
        });
    }});
        
});