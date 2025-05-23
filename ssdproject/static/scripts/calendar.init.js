
$(function () {
    "use strict";

    function initFullCalendar() {
        function addEvent(name, date, index) {
            var html = `
                <li data-index="${index}">
                    <input class="event-name" value="${name}">
                    <div class="event-date">${date}</div>
                    <div class="event-remove-icon ion ion-trash-a removeEventBtn"></div>
                </li>`;
            $("#calevents").append(html);
        }

        function removeEvent(calEvent) {
            calEvent.remove();
            FC.fullCalendar("removeEvents", function (eventObject) {
                return eventObject.title === calEvent.find(".event-name").val();
            });
        }

        function changeView(view) {
            FC.fullCalendar("changeView", view);
            calToolbar.find(".current-date").html(FC.fullCalendar("getView").title);
        }

        function prev() {
            FC.fullCalendar("prev");
            calToolbar.find(".current-date").html(FC.fullCalendar("getView").title);
        }

        function next() {
            FC.fullCalendar("next");
            calToolbar.find(".current-date").html(FC.fullCalendar("getView").title);
        }

        function today() {
            FC.fullCalendar("today");
            calToolbar.find(".current-date").html(FC.fullCalendar("getView").title);
        }

        var date = new Date(),
            d = date.getDate(),
            m = date.getMonth(),
            y = date.getFullYear();

        var calEvents = [
            { title: "All Day Event", start: new Date(y, m, 1) },
            { title: "Very Long Event", start: new Date(y, m, d + 10, 11, 22), end: new Date(y, m, d + 13), className: "bg-primary", description: "Short description about event" },
            { id: 999, title: "Repeating Event", start: new Date(y, m, d - 3, 16, 33), allDay: false, className: "bg-danger" },
            { title: "Repeating Event", start: new Date(y, m, d + 4, 13, 45), className: "bg-warning" },
            { title: "Birthday Party", start: new Date(y, m, d + 1, 19, 0), end: new Date(y, m, d + 1, 22, 30), allDay: false, description: "Come to my birthday.", className: "bg-info" },
            { title: "Click for Google", start: new Date(y, m, 28), end: new Date(y, m, 29), url: "http://google.com/", className: "bg-success" }
        ];

        var FC = $("#fullCalendar").fullCalendar({
            height: 480,
            editable: true,
            defaultView: "month",
            header: false,
            eventLimit: true,
            events: calEvents
        });

        var calToolbar = $(".calendar-toolbar");
        calToolbar.find(".current-date").html(moment().format("MMMM YYYY"));

        calEvents.forEach(function (event, index) {
            addEvent(event.title, moment(event.start).format("MMM DD") + " - " + moment(event.end).format("MMM DD"), index);
        });

        calToolbar.find(".prev-btn").on("click touchstart", prev);
        calToolbar.find(".next-btn").on("click touchstart", next);
        calToolbar.find(".today-btn").on("click touchstart", today);

        calToolbar.find(".view-month").on("click touchstart", function () { changeView("month"); });
        calToolbar.find(".view-week").on("click touchstart", function () { changeView("agendaWeek"); });
        calToolbar.find(".view-day").on("click touchstart", function () { changeView("agendaDay"); });

        $(".addEventBtn").on("click touchstart", function (e) {
            var startDate = new Date(y, m, d);
            addEvent("New Event", moment(startDate).format("MMM DD") + " - ");
            FC.fullCalendar("renderEvent", { start: startDate, title: "New Event" });
            e.preventDefault();
        });

        $(document).on("click touchstart", ".removeEventBtn", function (e) {
            e.preventDefault();
            var calEvent = $(this).parent("li");
            removeEvent(calEvent);
        });
    }

    function _init() {
        initFullCalendar();
    }

    _init();
});
