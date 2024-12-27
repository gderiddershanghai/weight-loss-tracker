document.addEventListener("DOMContentLoaded", async () => {
    const response = await fetch("static/data.json");


    const { dates, raw_values, cumulative_values, projections } = await response.json();

    // Combine actual data and projections into one dataset
    const users = Object.keys(cumulative_values);
    const goals = {
        "Fifi": -5, "Sofya": -4, "Nick": -4, "Blue": -5, "Joyce": -5,
        "Jenny": -5, "Yoyo": -8, "Jimmy": -5, "Jerry": -5, "Summer G": -10,
        "Barry": -8, "Esther": -8, "Ginger": -10, "Mia": -10
    };
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
        })),
        goal: { date: "01.16", value: goals[user] } // Assuming the goal date is consistent for all users
    }));
    // Example assuming 'dates' is already defined and "01.16" needs to be added
    if (!dates.includes("01.15")) {
        dates.push("----");
    ; // Ensure the dates are in chronological order if necessary
    }

    if (!dates.includes("01.16")) {
        dates.push("01.16");
    ; // Ensure the dates are in chronological order if necessary
    }

    // Dimensions
    const margin = { top: 30, right: 100, bottom: 50, left: 50 };
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
        .attr("viewBox", `0 0 ${800} ${400}`) // Set initial width and height
        .attr("preserveAspectRatio", "xMidYMid meet") // Ensure proper scaling
        .classed("responsive-svg", true) // Optional: Add a class for styling
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
    .call(d3.axisBottom(xScale))
    .selectAll("text")
    .style("font-size", "calc(0.8em + 0.5vw)"); // Scales based on viewport width

// Add a title to the chart
svg.append("text")
    .attr("x", (width + margin.left + margin.right) / 2) // Center horizontally
    .attr("y", -margin.top / 2) // Position above the chart
    .attr("text-anchor", "middle") // Center the text
    .style("font-size", "16px") // Adjust font size
    .style("font-weight", "bold") // Make it bold
    .text("Weight Loss December-January"); // Replace with your desired title


    svg.append("g")
        .call(d3.axisLeft(yScale));

    // Color palette
    const colorPalette = [
        "#F8766D", "#A3A500", "#00BF7D", "#00B0F6", "#E76BF3",
        "#FA8867", "#AB8B00", "#39B185", "#00ACC1", "#C77CFF",
        "#8E9A80", "#BC3C29", "#FFA931", "#B3DE69", "#66C2A5"
    ];
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
    .style("display", "none"); // Keep this

    const goalPoints = svg.selectAll(".goal-point")
    .data(data.map(d => ({ ...d.goal, name: d.name })))
    .enter()
    .append("circle")
    .attr("class", "goal-point")
    .attr("cx", d => xScale(d.date))
    .attr("cy", d => yScale(d.value))
    .attr("r", 5)
    .attr("fill", d => color(d.name))
    .style("display", "none"); // Initialize with hidden visibility




// Add the tooltip behavior here:
actualPoints.on("mouseover", (event, d) => {
    const tooltip = d3.select("body").append("div")
        .attr("class", "tooltip")
        .style("position", "absolute")
        .style("background", "#fff")
        .style("border", "1px solid #ccc")
        .style("padding", "5px")
        .style("pointer-events", "none")
        .html(`Date: ${d.date}<br>变化: ${d.raw.toFixed(2)}`);

    tooltip.style("left", `${event.pageX + 5}px`)
           .style("top", `${event.pageY - 28}px`);
}).on("mouseout", () => d3.select(".tooltip").remove());

const projectionPoints = lines.selectAll(".projection-point")
    .data(d => d.projection.map(v => ({ ...v, name: d.name })))
    .enter()
    .append("circle")
    .attr("class", "projection-point")
    .attr("cx", v => xScale(v.date))
    .attr("cy", v => yScale(v.projection))
    .attr("r", 4)
    .attr("fill", v => color(v.name))
    .style("display", "none"); // Keep this

// Add the tooltip behavior here:
projectionPoints.on("mouseover", (event, d) => {
    const tooltip = d3.select("body").append("div")
        .attr("class", "tooltip")
        .style("position", "absolute")
        .style("background", "#fff")
        .style("border", "1px solid #ccc")
        .style("padding", "5px")
        .style("pointer-events", "none")
        .html(`Date: ${d.date}<br>预测: ${d.projection.toFixed(2)}`);

    tooltip.style("left", `${event.pageX + 5}px`)
           .style("top", `${event.pageY - 28}px`);
}).on("mouseout", () => d3.select(".tooltip").remove());


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

    function highlightLine(selectedName) {
        // Highlight the selected line and dim others
        lines.selectAll(".line")
            .style("opacity", d => d.name === selectedName ? 1 : 0.2);
        lines.selectAll(".projection-line")
            .style("opacity", d => d.name === selectedName ? 1 : 0.2);
        lines.selectAll(".connection-line")
            .style("opacity", d => d.name === selectedName ? 1 : 0.2);
    
        // Show scatter points for the selected user
        actualPoints.style("display", d => d.name === selectedName ? "block" : "none");
        projectionPoints.style("display", d => d.name === selectedName ? "block" : "none");
        goalPoints.style("display", d => d.name === selectedName ? "block" : "none");
        // Dim other legend items
        legend.style("opacity", d => d.name === selectedName ? 1 : 0.2);
    }
    

    // Reset highlights and hide scatter points
    function resetHighlight() {
        // Reset line visibility
        lines.selectAll(".line").style("opacity", 1);
        lines.selectAll(".projection-line").style("opacity", 1);
        lines.selectAll(".connection-line").style("opacity", 1);
    
        // Hide all scatter points
        actualPoints.style("display", "none");
        projectionPoints.style("display", "none");
    
        // Reset legend opacity
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