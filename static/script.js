document.addEventListener("DOMContentLoaded", async () => {
    const response = await fetch("static/data.json");

    const { dates, raw_values, cumulative_values, projections } = await response.json();

    // Combine actual data and projections into one dataset
    const users = Object.keys(cumulative_values);
    const data = users.map(user => ({
        name: user,
        actual: dates.slice(0, raw_values[user].length).map((date, i) => ({
            date,
            cumulative: cumulative_values[user][i],
            raw: raw_values[user][i]
        })),
        projection: dates.slice(raw_values[user].length).map((date, i) => ({
            date,
            projection: projections[user][i]
        }))
    }));

    // Dimensions
    const margin = { top: 50, right: 150, bottom: 50, left: 50 };
    const width = 800 - margin.left - margin.right;
    const height = 400 - margin.top - margin.bottom;

    // Scales
    const xScale = d3.scalePoint()
        .domain(dates)
        .range([0, width]);

    const yScale = d3.scaleLinear()
        .domain([4, -12]) // Fixed y-axis range
        .range([0, height]);

    // SVG Canvas
    const svg = d3.select("#chart")
        .append("svg")
        .attr("width", width + margin.left + margin.right)
        .attr("height", height + margin.top + margin.bottom)
        .append("g")
        .attr("transform", `translate(${margin.left},${margin.top})`);

    // Add gridlines
    const gridlinesX = d3.axisBottom(xScale)
        .tickSize(-height)
        .tickFormat("");

    const gridlinesY = d3.axisLeft(yScale)
        .tickSize(-width)
        .tickFormat("");

    svg.append("g")
        .attr("class", "grid")
        .attr("transform", `translate(0,${height})`)
        .call(gridlinesX)
        .selectAll("line")
        .style("stroke", "rgba(0, 0, 0, 0.3)")
        .style("stroke-dasharray", "4,4");

    svg.append("g")
        .attr("class", "grid")
        .call(gridlinesY)
        .selectAll("line")
        .style("stroke", "rgba(0, 0, 0, 0.3)")
        .style("stroke-dasharray", "4,4");

    // Axes
    svg.append("g")
        .attr("transform", `translate(0,${height})`)
        .call(d3.axisBottom(xScale));

    svg.append("g")
        .call(d3.axisLeft(yScale));

    // Color palette
    const colorPalette = d3.schemeTableau10.filter(color => color !== "#ffcc00");
    const color = d3.scaleOrdinal()
        .domain(users)
        .range(colorPalette);

    // Add actual data lines
    const lines = svg.selectAll(".line-group")
        .data(data)
        .enter()
        .append("g")
        .attr("class", "line-group");

    lines.append("path")
        .attr("class", "line")
        .attr("d", d => d3.line()
            .x(v => xScale(v.date))
            .y(v => yScale(v.cumulative))(d.actual))
        .attr("fill", "none")
        .attr("stroke", d => color(d.name))
        .attr("stroke-width", 2);

    // Add projection lines
    lines.append("path")
        .attr("class", "projection-line")
        .attr("d", d => d3.line()
            .defined(v => v.projection !== null)
            .x(v => xScale(v.date))
            .y(v => yScale(v.projection))(d.projection))
        .attr("fill", "none")
        .attr("stroke", d => color(d.name))
        .attr("stroke-width", 2)
        .style("stroke-dasharray", "4,4");

    // Add dashed connection between last actual data point and first projection
    lines.append("line")
        .attr("class", "connection-line")
        .attr("x1", d => xScale(d.actual[d.actual.length - 1].date))
        .attr("y1", d => yScale(d.actual[d.actual.length - 1].cumulative))
        .attr("x2", d => xScale(d.projection[0].date))
        .attr("y2", d => yScale(d.projection[0].projection))
        .attr("stroke", d => color(d.name))
        .attr("stroke-width", 2)
        .style("stroke-dasharray", "4,4");

    // Add scatter points for actual data
    const actualPoints = lines.selectAll(".actual-point")
        .data(d => d.actual.map(v => ({ ...v, name: d.name })))
        .enter()
        .append("circle")
        .attr("class", "actual-point")
        .attr("cx", v => xScale(v.date))
        .attr("cy", v => yScale(v.cumulative))
        .attr("r", 4)
        .attr("fill", v => color(v.name))
        .style("display", "none") // Hidden initially
        .on("mouseover", (event, d) => {
            const tooltip = d3.select("body").append("div")
                .attr("class", "tooltip")
                .style("position", "absolute")
                .style("background", "#fff")
                .style("border", "1px solid #ccc")
                .style("padding", "5px")
                .style("pointer-events", "none")
                .html(`Date: ${d.date}<br>体重变化: ${d.raw.toFixed(2)}`);

            tooltip.style("left", `${event.pageX + 5}px`).style("top", `${event.pageY - 28}px`);
        })
        .on("mouseout", () => d3.select(".tooltip").remove());

    // Add scatter points for projections
    const projectionPoints = lines.selectAll(".projection-point")
        .data(d => d.projection.map(v => ({ ...v, name: d.name })))
        .enter()
        .append("circle")
        .attr("class", "projection-point")
        .attr("cx", v => xScale(v.date))
        .attr("cy", v => yScale(v.projection))
        .attr("r", 4)
        .attr("fill", v => color(v.name))
        .style("display", "none") // Hidden initially
        .on("mouseover", (event, d) => {
            const tooltip = d3.select("body").append("div")
                .attr("class", "tooltip")
                .style("position", "absolute")
                .style("background", "#fff")
                .style("border", "1px solid #ccc")
                .style("padding", "5px")
                .style("pointer-events", "none")
                .html(`Date: ${d.date}<br>预测: ${d.projection.toFixed(2)}`);

            tooltip.style("left", `${event.pageX + 5}px`).style("top", `${event.pageY - 28}px`);
        })
        .on("mouseout", () => d3.select(".tooltip").remove());

    // Add legend
    const legend = svg.selectAll(".legend")
        .data(data)
        .enter()
        .append("g")
        .attr("class", "legend")
        .attr("transform", (d, i) => `translate(${width + 20},${i * 20})`)
        .style("cursor", "pointer");

    legend.append("rect")
        .attr("width", 10)
        .attr("height", 10)
        .attr("fill", d => color(d.name));

    legend.append("text")
        .attr("x", 20)
        .attr("y", 10)
        .text(d => d.name)
        .style("font-size", "12px")
        .attr("alignment-baseline", "middle");

    // Highlight selected line and show scatter points
    function highlightLine(selectedName) {
        lines.selectAll(".line")
            .style("opacity", d => d.name === selectedName ? 1 : 0.2);
        lines.selectAll(".projection-line")
            .style("opacity", d => d.name === selectedName ? 1 : 0.2);
        lines.selectAll(".connection-line")
            .style("opacity", d => d.name === selectedName ? 1 : 0.2);
        actualPoints.style("display", d => d.name === selectedName ? "block" : "none");
        projectionPoints.style("display", d => d.name === selectedName ? "block" : "none");
        legend.style("opacity", d => d.name === selectedName ? 1 : 0.2);
    }

    // Reset highlights and hide scatter points
    function resetHighlight() {
        lines.selectAll(".line").style("opacity", 1);
        lines.selectAll(".projection-line").style("opacity", 1);
        lines.selectAll(".connection-line").style("opacity", 1);
        actualPoints.style("display", "none");
        projectionPoints.style("display", "none");
        legend.style("opacity", 1);
    }

    // Add click events for legend
    legend.on("click", (event, d) => highlightLine(d.name));
    svg.on("dblclick", resetHighlight);
});

// Reset highlights when clicking outside the chart
document.addEventListener("click", (event) => {
    const chartElement = document.querySelector("#chart svg");
    if (!chartElement.contains(event.target)) {
        resetHighlight();
    }
});