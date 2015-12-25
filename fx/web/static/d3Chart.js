// request the data
d3.json("/historic/GBPUSD",
    function(error, ticks) {
        display(ticks);
    }
);

// Set the dimensions of the canvas / graph
var margin = {top: 0, right: 20, bottom: 30, left: 50},
    width = 900 - margin.left - margin.right,
    height = 300 - margin.top - margin.bottom;

// Set the ranges
var x = d3.time.scale().range([0, width]);
var y = d3.scale.linear().range([height, 0]);

// Define the axes
var xAxis = d3.svg.axis().scale(x)
    .orient("bottom").ticks(5)
    .tickFormat(d3.time.format("%d/%m/%y-%H:%M"));

var yAxis = d3.svg.axis().scale(y)
    .orient("left").ticks(5);

// Define the Bid line
var valueline = d3.svg.line()
    .x(function(d) { return x(d.DateTime); })
    .y(function(d) { return y(d.Bid); });

// Define the Ask line
var valueline2 = d3.svg.line()
    .x(function(d) { return x(d.DateTime); })
    .y(function(d) { return y(d.Ask); });

// Adds the svg canvas
var svg = d3.select("#chart1")
    .append("svg")
        .attr("width", width + margin.left + margin.right)
        .attr("height", height + margin.top + margin.bottom)
    .append("g")
        .attr("transform",
              "translate(" + margin.left + "," + margin.top + ")");


function display(ticks) { //rename to format datetime
    var parseDate = d3.time.format("%d-%b-%Y %H:%M:%S.%L").parse;
    ticks.forEach(function(tick) {
            tick.DateTime = tick.DateTime.substring(0,23);
            tick.DateTime = parseDate(tick.DateTime);
        }
    )
// Scale the range of the data
    x.domain(d3.extent(ticks, function(d) { return d.DateTime; }));
    yMin = d3.min(ticks, function(d) { return d.Bid; }); //bid always < ask
    yMax = d3.max(ticks, function(d) { return d.Ask; }); // ask always > bid
    y.domain([yMin, yMax]);

    // Add the valueline path.
    svg.append("path")
        .attr("class", "line")
        .attr("d", valueline(ticks));

    // Add the valueline path.
    svg.append("path")
        .attr("class", "line")
        .attr("d", valueline2(ticks))
        .style("stroke", "red");

    // Add the X Axis
    svg.append("g")
        .attr("class", "x axis")
        .attr("transform", "translate(0," + height + ")")
        .call(xAxis);

    // Add the Y Axis
    svg.append("g")
        .attr("class", "y axis")
        .call(yAxis);

//    svg.append("text")
//        .attr("x", (width / 2))
//        .attr("y", 0 - (margin.top / 2))
//        .attr("text-anchor", "middle")
//        .style("font-size", "16px")
//        .style("text-decoration", "underline")
//        .text("GBP/USD ('the cable'), over time");
//
//    legend = svg.append("g")
//      .attr("class","legend")
//      .attr("transform","translate(50,30)")
//      .style("font-size","12px")
//      .call(d3.legend);
}