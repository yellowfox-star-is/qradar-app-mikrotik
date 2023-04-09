var top_affix = "_top"
var bot_affix = "_bot"
var raw_affix = "_raw"
var offenses_affix = "_offenses"
var timeline_affix = "_timeline"
const nbsp = String.fromCharCode(160);

function create_top_element(id, name)
{
    let top_element = document.createElement("button")
    top_element.className = "accordion"
    top_element.id = id
    top_element.innerText = name
    top_element.addEventListener("click", accordion_collapse)
    return top_element
}

function create_bot_element(id)
{
    let bot_element = document.createElement("div")
    bot_element.className = 'panel'
    bot_element.id = id
    return bot_element
}


function create_element_pair(id, name)
{
    let top_element = create_top_element(id + top_affix, name)
    let bot_element = create_bot_element(id + bot_affix)
    return [top_element, bot_element]
}

function insert_element_pair(target, pair)
{
    target.appendChild(pair[0])
    target.appendChild(pair[1])
}

function update_number(target_element, new_number)
{
    target_element.innerText = target_element.innerText.replace(/^\d+?\s+/, '')
    target_element.innerText = new_number + " " + target_element.innerText
}

function update_offenses_element(router_name)
{
    // get offenses

    let offenses_element = document.getElementById(router_name + '_offenses_bot')
    update_number(document.getElementById(router_name + offenses_affix + top_affix), router['offenses'].length)
    offenses_element.innerHTML = '' // clear previous offenses
    for (const offense of offenses)
    {
        // TODO add some totally superb processing here
        continue
    }
}

function create_router(root_element, router)
{
    let router_name = router['name']

    // prepare offenses
    let offenses_elements = create_element_pair(router_name + offenses_affix, "Offenses")

    // prepare raw
    let raw_elements = create_raw_elements(router_name)

    // prepare timeline
    let timeline_elemets = create_element_pair(router_name + timeline_affix, 'Timeline')

    // create router
    let router_elements = create_element_pair(router_name, router_name)

    // fill router
    insert_element_pair(router_elements[1], timeline_elemets)
    insert_element_pair(router_elements[1], raw_elements)
    insert_element_pair(router_elements[1], offenses_elements)

    // wrap it up by inserting into target
    insert_element_pair(root_element, router_elements)
}

function create_router_elements(root_id, data)
{
    let root_element = document.getElementById(root_id)
    for (const router of data)
    {
        create_router(root_element, router)
    }
}

function update_router(root_element, router)
{
    let router_name = router['name']
    let router_element = get_router_element_bot(router_name)

    update_offenses_element(router_name)
    update_raw_container(router)
    make_timeline(router)
}

function get_router_element_top(router_name)
{
    return document.getElementById(router_name + top_affix)
}

function get_router_element_bot(router_name)
{
    return document.getElementById(router_name + bot_affix)
}

function get_router_elements(router_name)
{
    let router_el_top = get_router_element_top(router_name)
    let router_el_bot = get_router_element_bot(router_name)
}

function update_router_elements(root_id, json_string)
{
    const data = JSON.parse(json_string);
    let root_element = document.getElementById(root_id)
    for (const router of data)
    {
        if (get_router_element_top(router['name']))
        {
            update_router(root_element, router)
        }
        else
        {
            create_router(root_element, router)
        }
    }
}

function create_raw_elements(router_name)
{
    let raw_elements = create_element_pair(router_name + raw_affix, 'Logs')
    raw_elements[1].classList.add('raw_container')
    return raw_elements
}

function element_exists(element_id)
{
    return document.getElementById(element_id) !== null
}

// REUSED CODE
// generated by ChatGPT, verified by YellowFox
function format_timestamp(timestamp)
{
    const date = new Date(timestamp);

    const day = date.getDate().toString().padStart(2, '0');
    const month = (date.getMonth() + 1).toString().padStart(2, '0'); // month is zero-based, so add 1
    const year = date.getFullYear().toString();
    const hours = date.getHours().toString().padStart(2, '0');
    const minutes = date.getMinutes().toString().padStart(2, '0');
    const seconds = date.getSeconds().toString().padStart(2, '0');

    const formattedDate = `${day}/${month}/${year}, ${hours}:${minutes}:${seconds}`;

    return formattedDate
}

function update_raw_container(router)
{
    // WARNING need to check scrolling

    let raw_container = document.getElementById(router.name + raw_affix + bot_affix)
    fetch('/get/raw/' + router.id)
        .then((response) => response.json())
        .then((data) =>
            {
                for (const payload of data)
                {
                    if (element_exists(payload.id))
                    {
                        continue
                    }

                    const payload_element = document.createElement('div')
                    payload_element.id = payload.id
                    payload_element.innerHTML = format_timestamp(payload.timestamp) + " &emsp;&emsp; " + payload.payload
                    raw_container.appendChild(payload_element)
                }
            }
        )

    // probably scroll here?
}

function update_raw_containers()
{
    fetch('/get/routers')
        .then((response) => response.json())
        .then((data) =>
        {
            for (const router of data)
            {
                update_raw_container(router)
            }
        })
}


/*
FIXME Timeline start and end datetime doesn't show up in the HTML, now idea why, non-critical to fix
 */
function timeline(el, data)
/*
Copyright (c) 2023 by Andrew Borisenko (https://codepen.io/Seigiard/pen/MWwoqQ)

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

Code obtained from Andrew Borisenko
translated from jQuery to vanilla JavaScript by ChatGPT
fixed and modified by Yellow Fox
 */
{
    el.classList.add("timeline");
    // calc ratio for event positions
    const ratio = 100 / (data.stop_time - data.start_time);

    data.lines.forEach(function (line)
    {
        const lineTmpl = document.createElement("div");
        lineTmpl.innerHTML =
            '<h4>' +
            line.title +
            '</h4><div class="events"></div>';
        lineTmpl.classList.add("line", line.css);
        el.appendChild(lineTmpl);

        line.events.forEach(function (event)
        {
            const position = ((event.time - data.start_time) * ratio).toFixed(2);

            const eventTmpl = document.createElement("div");
            eventTmpl.classList.add('event')
            eventTmpl.innerHTML =
                '<div class="circle"><div class="circle-inner"></div><div class="label"><label>' +
                event.title +
                "</label><time>" +
                new Date(event.time).toLocaleString() +
                "</time></div></div>";
            eventTmpl.style.left = position + "%";
            lineTmpl.querySelector(".events").appendChild(eventTmpl);
        });
    });

    const timeTmpl = document.createElement("div");
    timeTmpl.classList.add("time");
    el.appendChild(timeTmpl);

    const periodTmpl = document.createElement("div");
    periodTmpl.classList.add('period')
    periodTmpl.innerHTML =
        '<div class="label last">' +
        new Date(data.stop_time).toLocaleString() +
        '</div><div class="label first">' +
        new Date(data.start_time).toLocaleString() +
        "</div>";
    periodTmpl.style.left = "0%";
    periodTmpl.style.width = "100%";
    timeTmpl.appendChild(periodTmpl);
}

function make_timeline(router)
{

                fetch('/get/timeline/' + router['id'])
                    .then((response) => response.json())
                    .then((data) =>
                    {
    let target_element = document.getElementById(router['name'] + timeline_affix + bot_affix)

    let timeline_element = document.createElement('div')
    timeline_element.classList.add('tl')
    timeline(timeline_element, data)
    target_element.appendChild(timeline_element)
                    })
}

function make_timelines()
{
    fetch('/get/routers')
        .then((response) => response.json())
        .then((data) =>
        {
            for (const router of data)
            {
                make_timeline(router)
            }
        })
}