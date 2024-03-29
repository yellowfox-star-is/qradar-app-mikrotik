/*
Copyright (c) 2023 by Andrew Borisenko (https://codepen.io/Seigiard/pen/MWwoqQ)

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
 */

/*
Edited by Yellow Fox
 */


(function ($) {
  $.fn.timeline = function (data) {
    return this.each(function () {
      $el = $(this);
      $el.addClass("timeline");

      // calc ratio for event positions
      var ratio = 100 / (data.stop_time - data.start_time);

      $.each(data.lines, function (i, line) {
        var lineTmpl = $(
          '<div class="line"><h4>' +
            line.title +
            '</h4><div class="events"></div></div>'
        )
          .addClass("line " + line.css)
          .appendTo($el);

        $.each(line.events, function (index, event) {
          var position = ((event.time - data.start_time) * ratio).toFixed(2);

          var eventTmpl = $(
            '<div class="event"><div class="circle"><div class="circle-inner"></div><div class="label"><label>' +
              event.title +
              "</label><time>" +
              new Date(event.time).toLocaleString() +
              "</time></div></div></div>"
          )
            .appendTo($(".events", lineTmpl))
            .css("left", position + "%");
        });
      });

      var timeTmpl = $('<div class="time">').appendTo($el);
      var periodTmpl = $(
        '<div class="period"><div class="label last">' +
          new Date(data.stop_time).toLocaleString() +
          '</div><div class="label first">' +
          new Date(data.start_time).toLocaleString() +
          "</div></div>"
      )
        .css({ left: "0%", width: "100%" })
        .appendTo(timeTmpl);
    });
  };

  var data = {
    start_time: 90000,
    stop_time: 120000,
    lines: {
      checklists: {
        title: "Checklists",
        css: "checklist",
        events: [
          {
            id: 1,
            type: "start_work",
            time: 92000,
            title: "Start Work",
            status: "complete",
            description: "O-la-la"
          },
          {
            id: 2,
            type: "vehicle",
            time: 95000,
            title: "Vehicle",
            status: "complete",
            description: "O-la-la"
          },
          {
            id: 3,
            type: "fuel",
            time: 101500,
            title: "Vehicle",
            status: "resolve",
            description: "O-la-la"
          },
          {
            id: 4,
            type: "trailer_pickup",
            time: 105000,
            title: "Trailer Pickup",
            status: "complete",
            description: "O-la-la"
          },
          {
            id: 5,
            type: "hms",
            time: 107000,
            title: "Danger situation",
            status: "alert",
            description: "O-la-la"
          },
          {
            id: 6,
            type: "trailer_delivery",
            time: 110000,
            title: "Trailer delivery ",
            status: "complete",
            description: "O-la-la"
          }
        ]
      },
      liquids: {
        title: "Fuel Filling",
        css: "liquid",
        events: [
          {
            id: 1,
            type: "start_work",
            time: 90500,
            title: "Start Work",
            status: "complete",
            description: "O-la-la"
          },
          {
            id: 2,
            type: "vehicle",
            time: 96000,
            title: "Vehicle",
            status: "complete",
            description: "O-la-la"
          },
          {
            id: 3,
            type: "fuel",
            time: 98000,
            title: "Vehicle",
            status: "resolve",
            description: "O-la-la"
          },
          {
            id: 4,
            type: "trailer_pickup",
            time: 103000,
            title: "Trailer Pickup",
            status: "complete",
            description: "O-la-la"
          },
          {
            id: 5,
            type: "hms",
            time: 105000,
            title: "Danger situation",
            status: "alert",
            description: "O-la-la"
          },
          {
            id: 6,
            type: "trailer_delivery",
            time: 118000,
            title: "Trailer delivery ",
            status: "complete",
            description: "O-la-la"
          }
        ]
      },
      hms: {
        title: "Alerts",
        css: "hms",
        events: [
          {
            id: 1,
            type: "start_work",
            time: 90000,
            title: "Start Work",
            status: "complete",
            description: "O-la-la"
          },
          {
            id: 2,
            type: "start_work",
            time: 100000,
            title: "Start Work",
            status: "complete",
            description: "O-la-la"
          },
          {
            id: 3,
            type: "vehicle",
            time: 115000,
            title: "Vehicle",
            status: "complete",
            description: "O-la-la"
          }
        ]
      }
    }
  };

  $(".tl").timeline(data);
})(jQuery);


$.fn.timeline = function (data) {
    return this.each(function () {
      $el = $(this);
      $el.addClass("timeline");

      // calc ratio for event positions
      var ratio = 100 / (data.stop_time - data.start_time);

      $.each(data.lines, function (i, line) {
        var lineTmpl = $(
          '<div class="line"><h4>' +
            line.title +
            '</h4><div class="events"></div></div>'
        )
          .addClass("line " + line.css)
          .appendTo($el);

        $.each(line.events, function (index, event) {
          var position = ((event.time - data.start_time) * ratio).toFixed(2);

          var eventTmpl = $(
            '<div class="event"><div class="circle"><div class="circle-inner"></div><div class="label"><label>' +
              event.title +
              "</label><time>" +
              new Date(event.time).toLocaleString() +
              "</time></div></div></div>"
          )
            .appendTo($(".events", lineTmpl))
            .css("left", position + "%");
        });
      });

      var timeTmpl = $('<div class="time">').appendTo($el);
      var periodTmpl = $(
        '<div class="period"><div class="label last">' +
          new Date(data.stop_time).toLocaleString() +
          '</div><div class="label first">' +
          new Date(data.start_time).toLocaleString() +
          "</div></div>"
      )
        .css({ left: "0%", width: "100%" })
        .appendTo(timeTmpl);
    });
  };