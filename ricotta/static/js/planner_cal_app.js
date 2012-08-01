$(function(){
    var Event = Backbone.Model.extend({
        idAttribute: "resource_uri",
        url: function() {
            return this.get('resource_uri') || this.collection.url;
        }
    });

    var Events = Backbone.Collection.extend({
        model: Event,
        url: PLANNER_API,
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
                   // left: 'prev,next today',
               //     center: 'title',
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
                allDaySlot: false,
                year: 2012,
                month: 8,
                date: 23
            });
        },
        addAll: function(){
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
        el: $("#prefDialog"),
        initialize: function() {
            _.bindAll(this);
        },
        render: function() {
            var buttons = {};
            if (this.model.isNew()) {
                _.extend(buttons, {'Save': this.save});
            } else {
                _.extend(buttons, {'Save': this.save,
                                   'Delete': this.destroy});
            }

            this.el.dialog({
                modal: true,
                title: (this.model.isNew() ? 'New' : 'Edit') + ' Planner Block',
                buttons: buttons,
                open: this.open,
            });

            return this;
        },
        open: function() {
            this.$("#prefBox option[value=" + this.model.get("title") +"]").attr("selected", "selected");
            
        },
        save: function() {
            this.model.set({'title': this.$("#prefBox option:selected").html()});
            switch (this.$("#prefBox option:selected").html())
            {
            case "Preferred":
                c = "Blue";
                break;
            case "In Class":
                c = "Orange";
                break;
            default:
                c = "Green";
                break;
            }
            this.model.set({'block_type': this.$("#prefBox").val(),
                            'worker': this.$("#user").val(),
                            'color': c})
             
            if (this.model.isNew()) {
                this.collection.create(this.model, {success: this.close});
            } else {
                this.model.save({}, {success: this.close});
            }
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
});