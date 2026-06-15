(() => {
    const svg = document.getElementById("builder-svg");
    const inspector = document.getElementById("component-inspector");
    const resultBox = document.getElementById("builder-result");
    const topologySelect = document.getElementById("builder-topology");
    const modeLabel = document.getElementById("builder-mode-label");
    const instruction = document.getElementById("builder-instruction");
    console.log("NEW BUILDER LOADED");

    if (!svg) return;

    let components = [];
    let wires = [];
    let selectedId = null;
    let connectionStart = null;
    let mode = "select";
    let dragState = null;
    let nextId = 1;
    const GRID = 80;

    const clamp = (value, minimum, maximum) =>
        Math.max(minimum, Math.min(maximum, value));

    function svgPoint(event) {
        const point = svg.createSVGPoint();
        point.x = event.clientX;
        point.y = event.clientY;
        return point.matrixTransform(svg.getScreenCTM().inverse());
    }

    function componentById(id) {
        return components.find((item) => item.id === id);
    }

    function sourceComponent() {
        return components.find((item) => item.type === "source");
    }

    function resistorComponents() {
        return components.filter((item) => item.type === "resistor");
    }

    function renumber() {
        let resistorNumber = 1;
        components.forEach((component) => {
            if (component.type === "source") {
                component.name = component.name || "V1";
            } else {
                if (!component.name || /^R\d+$/.test(component.name)) {
                    component.name = `R${resistorNumber}`;
                }
                resistorNumber += 1;
            }
        });
    }

    function addComponent(type, x, y) {
        if (type === "source" && sourceComponent()) {
            window.alert("Only one voltage source is supported in this builder.");
            return;
        }

        const component = {
            id: `c${nextId++}`,
            type,
            name: type === "source" ? "V1" : "R1",
            value: type === "source" ? 12 : 10,
            x: Math.round(clamp(x, 90, 910) / GRID) * GRID,
            y: Math.round(clamp(y, 90, 510) / GRID) * GRID,
            orientation: type === "source" ? "vertical" : "horizontal"
        };
        


        components.push(component);
        renumber();
        selectedId = component.id;
        renderAll();
    }

    function terminalPosition(component, terminal) {
        const offset = GRID;
    
        if (component.type === "source") {
            return terminal === "a"
                ? { x: component.x, y: component.y - offset }
                : { x: component.x, y: component.y + offset };
        }
    
        if (component.type === "resistor") {
            return terminal === "a"
                ? { x: component.x - offset, y: component.y }
                : { x: component.x + offset, y: component.y };
        }
    
        return { x: component.x, y: component.y };
    }

    function wirePath(wire) {
        const EPS = 0.5;
        const a = componentById(wire.from.id);
        const b = componentById(wire.to.id);
    
        const start = terminalPosition(a, wire.from.terminal);
        const end = terminalPosition(b, wire.to.terminal);
    
        // FORCE shared electrical node alignment
        const isVerticalDrop = Math.abs(start.x - end.x) < GRID;
    
        if (isVerticalDrop) {
            return `
                M ${start.x} ${start.y}
                L ${start.x} ${end.y}
            `;
        }
    
        return `
            M ${start.x + EPS} ${start.y + EPS}
            L ${start.x} ${end.y}
            L ${end.x} ${end.y}
        `;
    }
    function resistorMarkup(component) {
        if (component.orientation === "vertical") {
            return `
                <line x1="${component.x}" y1="${component.y - GRID}" x2="${component.x}" y2="${component.y - 42}" class="component-lead"></line>
                <path d="M ${component.x} ${component.y - 42}
                         L ${component.x} ${component.y - 34}
                         L ${component.x - 14} ${component.y - 25}
                         L ${component.x + 14} ${component.y - 12}
                         L ${component.x - 14} ${component.y + 1}
                         L ${component.x + 14} ${component.y + 14}
                         L ${component.x - 14} ${component.y + 27}
                         L ${component.x} ${component.y + 38}
                         L ${component.x} ${component.y + 42}"
                      class="builder-resistor"></path>
                <line x1="${component.x}" y1="${component.y + 42}" x2="${component.x}" y2="${component.y + 62}" class="component-lead"></line>
            `;
        }

        return `
            <line x1="${component.x - GRID}" y1="${component.y}" x2="${component.x - GRID/2}" y2="${component.y}" class="component-lead"></line>
        
            <path d="M ${component.x - GRID/2} ${component.y}
                     L ${component.x - 28} ${component.y}
                     L ${component.x - 18} ${component.y - 14}
                     L ${component.x - 6} ${component.y + 14}
                     L ${component.x + 6} ${component.y - 14}
                     L ${component.x + 18} ${component.y + 14}
                     L ${component.x + 28} ${component.y - 14}
                     L ${component.x + GRID/2} ${component.y}"
                  class="builder-resistor"></path>
        
            <line x1="${component.x + GRID/2}" y1="${component.y}" x2="${component.x + GRID}" y2="${component.y}" class="component-lead"></line>
        `;
    }

    function sourceMarkup(component) {
        return `
            <line x1="${component.x}" y1="${component.y - GRID}" x2="${component.x}" y2="${component.y - GRID/2}" class="component-lead"></line>
    
            <circle cx="${component.x}" cy="${component.y}" r="30" class="builder-source"></circle>
    
            <text x="${component.x}" y="${component.y - 10}" text-anchor="middle" class="builder-polarity">+</text>
            <text x="${component.x}" y="${component.y + 18}" text-anchor="middle" class="builder-polarity">-</text>
    
            <line x1="${component.x}" y1="${component.y + GRID/2}" x2="${component.x}" y2="${component.y + GRID}" class="component-lead"></line>
        `;
    }

    function componentMarkup(component) {
        const selectedClass = component.id === selectedId ? " selected-component" : "";
        const terminalA = terminalPosition(component, "a");
        const terminalB = terminalPosition(component, "b");
        const pendingA = connectionStart && connectionStart.id === component.id && connectionStart.terminal === "a";
        const pendingB = connectionStart && connectionStart.id === component.id && connectionStart.terminal === "b";

        return `
            <g class="builder-component-group${selectedClass}" data-component-id="${component.id}">
                ${component.type === "source" ? sourceMarkup(component) : resistorMarkup(component)}
                <text x="${component.x}" y="${component.y - GRID/2 - 10}" text-anchor="middle" class="builder-component-label">
                    ${component.name}=${component.value}${component.type === "source" ? "V" : "Ω"}
                </text>
                <circle cx="${terminalA.x}" cy="${terminalA.y}" r="8"
                    class="builder-terminal${pendingA ? " pending-terminal" : ""}"
                    data-component-id="${component.id}" data-terminal="a"></circle>
                <circle cx="${terminalB.x}" cy="${terminalB.y}" r="8"
                    class="builder-terminal${pendingB ? " pending-terminal" : ""}"
                    data-component-id="${component.id}" data-terminal="b"></circle>
            </g>
        `;
    }

    function renderCanvas() {
        const wireMarkup = wires.map((wire) => `
            <path d="${wirePath(wire)}" class="builder-wire"></path>
        `).join("");

        const componentMarkupText = components.map(componentMarkup).join("");

        svg.innerHTML = `
            <defs>
                <pattern id="smallGrid" width="20" height="20" patternUnits="userSpaceOnUse">
                    <path d="M 20 0 L 0 0 0 20" fill="none" stroke="#e7edf3" stroke-width="1"></path>
                </pattern>
                <pattern id="grid" width="100" height="100" patternUnits="userSpaceOnUse">
                    <rect width="100" height="100" fill="url(#smallGrid)"></rect>
                    <path d="M 100 0 L 0 0 0 100" fill="none" stroke="#d2dce6" stroke-width="1.4"></path>
                </pattern>
            </defs>
            <rect width="1000" height="600" fill="url(#grid)"></rect>
            ${wireMarkup}
            ${componentMarkupText}
            ${components.length === 0 ? `
                <text x="500" y="280" text-anchor="middle" class="svg-message">
                    Drag a voltage source and resistors from the palette onto this canvas.
                </text>
                <text x="500" y="315" text-anchor="middle" class="svg-message secondary-message">
                    Switch to Connect Terminals, then click two blue terminals to create a wire.
                </text>
            ` : ""}
        `;
    }

    function renderInspector() {
        const component = componentById(selectedId);
        if (!component) {
            inspector.innerHTML = `
                <div class="inspector-empty">
                    Select a component to edit its name, value or orientation.
                </div>
            `;
            return;
        }

        inspector.innerHTML = `
            <div class="inspector-grid">
                <div>
                    <p class="eyebrow">SELECTED COMPONENT</p>
                    <h2>${component.type === "source" ? "Voltage Source" : "Resistor"}</h2>
                </div>
                <label>
                    Name
                    <input id="inspector-name" value="${component.name}">
                </label>
                <label>
                    Value (${component.type === "source" ? "V" : "Ω"})
                    <input id="inspector-value" type="number" step="any" value="${component.value}">
                </label>
                ${component.type === "resistor" ? `
                    <button class="button" id="rotate-component" type="button">
                        Rotate ${component.orientation === "horizontal" ? "Vertical" : "Horizontal"}
                    </button>
                ` : ""}
            </div>
        `;

        document.getElementById("inspector-name").addEventListener("input", (event) => {
            component.name = event.target.value.trim() || component.name;
            renderCanvas();
        });

        document.getElementById("inspector-value").addEventListener("input", (event) => {
            const numericValue = Number(event.target.value);
            if (Number.isFinite(numericValue)) component.value = numericValue;
            renderCanvas();
        });

        const rotateButton = document.getElementById("rotate-component");
        if (rotateButton) {
            rotateButton.addEventListener("click", () => {
                component.orientation = component.orientation === "horizontal" ? "vertical" : "horizontal";
                renderAll();
            });
        }
    }

    function renderAll() {
        renderCanvas();
        renderInspector();
    }

    function setMode(newMode) {
        mode = newMode;
        connectionStart = null;
        document.getElementById("select-mode").classList.toggle("primary", mode === "select");
        document.getElementById("connect-mode").classList.toggle("primary", mode === "connect");

        if (mode === "select") {
            modeLabel.textContent = "Mode: Select / Move";
            instruction.textContent = "Click and drag components. Select one to edit it below.";
        } else {
            modeLabel.textContent = "Mode: Connect Terminals";
            instruction.textContent = "Click one blue terminal, then click the destination terminal.";
        }
        renderCanvas();
    }

    function connectTerminal(id, terminal) {
        if (!connectionStart) {
            connectionStart = { id, terminal };
            renderCanvas();
            return;
        }

        if (connectionStart.id === id && connectionStart.terminal === terminal) {
            connectionStart = null;
            renderCanvas();
            return;
        }

        const duplicate = wires.some((wire) => {
            const sameDirection = wire.from.id === connectionStart.id &&
                wire.from.terminal === connectionStart.terminal &&
                wire.to.id === id && wire.to.terminal === terminal;
            const reverseDirection = wire.to.id === connectionStart.id &&
                wire.to.terminal === connectionStart.terminal &&
                wire.from.id === id && wire.from.terminal === terminal;
            return sameDirection || reverseDirection;
        });

        if (!duplicate) {
            wires.push({
                from: { ...connectionStart },
                to: { id, terminal }
            });
        }

        connectionStart = null;
        renderCanvas();
    }

    function deleteSelected() {
        if (!selectedId) return;
        components = components.filter((component) => component.id !== selectedId);
        wires = wires.filter((wire) => wire.from.id !== selectedId && wire.to.id !== selectedId);
        selectedId = null;
        renumber();
        renderAll();
    }

    function ensureBasicComponents() {
        let source = sourceComponent();
        if (!source) {
            addComponent("source", 150, 300);
            source = sourceComponent();
        }
        if (resistorComponents().length === 0) {
            addComponent("resistor", 400, 180);
            addComponent("resistor", 650, 180);
        }
        return source;
    }

    function autoWireSeries() {
        topologySelect.value = "series";
        const source = ensureBasicComponents();
        const resistors = resistorComponents();
        wires = [];

        source.x = 140;
        source.y = 300;
        source.orientation = "vertical";

        const spacing = Math.min(220, 700 / Math.max(1, resistors.length));
        resistors.forEach((resistor, index) => {
            resistor.orientation = "horizontal";
            resistor.x = 280 + spacing * index;
            resistor.y = 150;
        });

        if (resistors.length) {
            wires.push({ from: { id: source.id, terminal: "a" }, to: { id: resistors[0].id, terminal: "a" } });
            for (let index = 0; index < resistors.length - 1; index += 1) {
                wires.push({ from: { id: resistors[index].id, terminal: "b" }, to: { id: resistors[index + 1].id, terminal: "a" } });
            }
            wires.push({ from: { id: resistors[resistors.length - 1].id, terminal: "b" }, to: { id: source.id, terminal: "b" } });
        }
        renderAll();
    }

    function autoWireParallel() {
        topologySelect.value = "parallel";
        const source = ensureBasicComponents();
        const resistors = resistorComponents();
        wires = [];

        source.x = 140;
        source.y = 300;
        source.orientation = "vertical";

        const spacing = Math.min(190, 650 / Math.max(1, resistors.length));
        resistors.forEach((resistor, index) => {
            resistor.orientation = "vertical";
            resistor.x = 350 + spacing * index;
            resistor.y = 300;
            wires.push({ from: { id: source.id, terminal: "a" }, to: { id: resistor.id, terminal: "a" } });
            wires.push({ from: { id: source.id, terminal: "b" }, to: { id: resistor.id, terminal: "b" } });
        });
        renderAll();
    }

    function calculate() {
        const source = sourceComponent();
        const resistors = resistorComponents();

        if (!source || resistors.length === 0) {
            window.alert("Add one voltage source and at least one resistor.");
            return;
        }
        if (source.value <= 0 || resistors.some((resistor) => resistor.value <= 0)) {
            window.alert("All component values must be greater than zero.");
            return;
        }

        let totalResistance;
        let totalCurrent;
        let rows;

        if (topologySelect.value === "series") {
            totalResistance = resistors.reduce((sum, resistor) => sum + resistor.value, 0);
            totalCurrent = source.value / totalResistance;
            rows = resistors.map((resistor) => ({
                ...resistor,
                voltage: totalCurrent * resistor.value,
                current: totalCurrent
            }));
        } else {
            totalResistance = 1 / resistors.reduce((sum, resistor) => sum + 1 / resistor.value, 0);
            totalCurrent = source.value / totalResistance;
            rows = resistors.map((resistor) => ({
                ...resistor,
                voltage: source.value,
                current: source.value / resistor.value
            }));
        }

        resultBox.innerHTML = `
            <h2>Calculated ${topologySelect.value[0].toUpperCase() + topologySelect.value.slice(1)} Design</h2>
            <div class="result-grid compact">
                <div><span>Total Resistance</span><strong>${totalResistance.toFixed(4)} Ω</strong></div>
                <div><span>Total Current</span><strong>${totalCurrent.toFixed(4)} A</strong></div>
            </div>
            <div class="table-scroll">
                <table>
                    <thead><tr><th>Component</th><th>Resistance</th><th>Voltage</th><th>Current</th></tr></thead>
                    <tbody>
                        ${rows.map((item) => `
                            <tr>
                                <td>${item.name}</td>
                                <td>${item.value.toFixed(4)} Ω</td>
                                <td>${item.voltage.toFixed(4)} V</td>
                                <td>${item.current.toFixed(4)} A</td>
                            </tr>
                        `).join("")}
                    </tbody>
                </table>
            </div>
        `;
    }

    document.querySelectorAll("[draggable='true']").forEach((item) => {
        item.addEventListener("dragstart", (event) => {
            event.dataTransfer.setData("text/plain", item.dataset.component);
        });
    });

    svg.addEventListener("dragover", (event) => {
        event.preventDefault();
        svg.classList.add("drag-over");
    });

    svg.addEventListener("dragleave", () => svg.classList.remove("drag-over"));

    svg.addEventListener("drop", (event) => {
        event.preventDefault();
        svg.classList.remove("drag-over");
        const type = event.dataTransfer.getData("text/plain");
        if (!["source", "resistor"].includes(type)) return;
        const point = svgPoint(event);
        addComponent(type, point.x, point.y);
    });

    svg.addEventListener("pointerdown", (event) => {
        const terminal = event.target.closest(".builder-terminal");
        if (terminal && mode === "connect") {
            event.stopPropagation();
            connectTerminal(terminal.dataset.componentId, terminal.dataset.terminal);
            return;
        }

        const group = event.target.closest(".builder-component-group");
        if (!group) {
            selectedId = null;
            renderAll();
            return;
        }

        selectedId = group.dataset.componentId;
        renderInspector();
        renderCanvas();

        if (mode !== "select") return;
        const component = componentById(selectedId);
        const point = svgPoint(event);
        dragState = {
            id: selectedId,
            offsetX: point.x - component.x,
            offsetY: point.y - component.y
        };
        svg.setPointerCapture(event.pointerId);
    });

    svg.addEventListener("pointermove", (event) => {
        if (!dragState) return;
        const component = componentById(dragState.id);
        if (!component) return;
        const point = svgPoint(event);
        component.x = clamp(point.x - dragState.offsetX, 85, 915);
        component.y = clamp(point.y - dragState.offsetY, 85, 515);
        component.x = Math.round(component.x / GRID) * GRID;
        component.y = Math.round(component.y / GRID) * GRID;
        renderCanvas();
    });

    svg.addEventListener("pointerup", (event) => {
        if (dragState) {
            dragState = null;
            try { svg.releasePointerCapture(event.pointerId); } catch (_error) {}
        }
    });

    document.addEventListener("keydown", (event) => {
        if (event.key === "Delete" || event.key === "Backspace") {
            const activeTag = document.activeElement?.tagName;
            if (activeTag !== "INPUT" && activeTag !== "TEXTAREA") {
                event.preventDefault();
                deleteSelected();
            }
        }
    });

    document.getElementById("select-mode").addEventListener("click", () => setMode("select"));
    document.getElementById("connect-mode").addEventListener("click", () => setMode("connect"));
    document.getElementById("delete-selected").addEventListener("click", deleteSelected);
    document.getElementById("auto-series").addEventListener("click", autoWireSeries);
    document.getElementById("auto-parallel").addEventListener("click", autoWireParallel);
    document.getElementById("calculate-design").addEventListener("click", calculate);

    document.getElementById("save-design").addEventListener("click", () => {
        localStorage.setItem("circuitTutorVisualDesignV2", JSON.stringify({
            components,
            wires,
            topology: topologySelect.value,
            nextId
        }));
        window.alert("Design saved in this browser.");
    });

    document.getElementById("load-design").addEventListener("click", () => {
        const saved = localStorage.getItem("circuitTutorVisualDesignV2");
        if (!saved) {
            window.alert("No saved design was found.");
            return;
        }
        try {
            const data = JSON.parse(saved);
            components = Array.isArray(data.components) ? data.components : [];
            wires = Array.isArray(data.wires) ? data.wires : [];
            topologySelect.value = data.topology || "series";
            nextId = Number(data.nextId) || components.length + 1;
            selectedId = null;
            connectionStart = null;
            renderAll();
        } catch (_error) {
            window.alert("The saved design could not be loaded.");
        }
    });

    document.getElementById("clear-design").addEventListener("click", () => {
        if (!window.confirm("Clear every component and wire?")) return;
        components = [];
        wires = [];
        selectedId = null;
        connectionStart = null;
        resultBox.innerHTML = `<div class="empty-state">Calculate the design to view electrical results.</div>`;
        renderAll();
    });

    topologySelect.addEventListener("change", () => {
        resultBox.innerHTML = `<div class="empty-state">Calculate the design to view electrical results.</div>`;
    });

    setMode("select");
    renderAll();
})();
