// MCP Client Interface

// Tool definitions
const tools = {
  calculator: {
    operations: ['add', 'subtract', 'multiply', 'divide', 'power'],
    params: {
      add: [
        { name: 'a', type: 'number', label: 'Number A' },
        { name: 'b', type: 'number', label: 'Number B' }
      ],
      subtract: [
        { name: 'a', type: 'number', label: 'Number A' },
        { name: 'b', type: 'number', label: 'Number B' }
      ],
      multiply: [
        { name: 'a', type: 'number', label: 'Number A' },
        { name: 'b', type: 'number', label: 'Number B' }
      ],
      divide: [
        { name: 'a', type: 'number', label: 'Number A' },
        { name: 'b', type: 'number', label: 'Number B (non-zero)' }
      ],
      power: [
        { name: 'a', type: 'number', label: 'Base' },
        { name: 'b', type: 'number', label: 'Exponent' }
      ]
    }
  },
  textProcessor: {
    operations: ['word_count', 'character_count', 'sentence_count', 'to_upper_case', 'to_lower_case'],
    params: {
      word_count: [
        { name: 'text', type: 'text', label: 'Text to analyze' }
      ],
      character_count: [
        { name: 'text', type: 'text', label: 'Text to analyze' }
      ],
      sentence_count: [
        { name: 'text', type: 'text', label: 'Text to analyze' }
      ],
      to_upper_case: [
        { name: 'text', type: 'text', label: 'Text to convert' }
      ],
      to_lower_case: [
        { name: 'text', type: 'text', label: 'Text to convert' }
      ]
    }
  },
  dataTransformer: {
    operations: ['json_to_csv', 'csv_to_json'],
    params: {
      json_to_csv: [
        { name: 'json_data', type: 'textarea', label: 'JSON data' }
      ],
      csv_to_json: [
        { name: 'csv_data', type: 'textarea', label: 'CSV data' }
      ]
    }
  }
};

// DOM Elements
const statusText = document.getElementById('status-text');
const sessionId = document.getElementById('session-id');
const initializeBtn = document.getElementById('initialize-btn');
const terminateBtn = document.getElementById('terminate-btn');
const promptInput = document.getElementById('prompt-input');
const processBtn = document.getElementById('process-btn');
const outputDisplay = document.getElementById('output-display');
const toolSelect = document.getElementById('tool-select');
const operationSelect = document.getElementById('operation-select');
const paramsContainer = document.getElementById('params-container');
const executeToolBtn = document.getElementById('execute-tool-btn');
const toolResult = document.getElementById('tool-result');
const notificationsDisplay = document.getElementById('notifications-display');

// Initialize the client
async function initializeClient() {
  try {
    initializeBtn.disabled = true;

    // Update status
    statusText.textContent = 'Initializing...';

    // Call initialize endpoint
    const response = await fetch('/initialize', {
      method: 'POST'
    });

    const result = await response.json();

    if (result.success) {
      // Update UI
      statusText.textContent = 'Connected';
      sessionId.textContent = result.sessionId;

      // Enable/disable buttons
      initializeBtn.disabled = true;
      terminateBtn.disabled = false;
      processBtn.disabled = false;
      executeToolBtn.disabled = false;

      addNotification('Client initialized successfully.', 'success');
    } else {
      statusText.textContent = 'Error';
      addNotification(`Initialization failed: ${result.error}`, 'error');
      initializeBtn.disabled = false;
    }
  } catch (error) {
    statusText.textContent = 'Error';
    addNotification(`Initialization error: ${error.message}`, 'error');
    initializeBtn.disabled = false;
  }
}

// Terminate the client
async function terminateClient() {
  try {
    terminateBtn.disabled = true;

    // Update status
    statusText.textContent = 'Terminating...';

    // Call terminate endpoint
    const response = await fetch('/terminate', {
      method: 'POST'
    });

    const result = await response.json();

    if (result.success) {
      // Update UI
      statusText.textContent = 'Disconnected';
      sessionId.textContent = 'None';

      // Enable/disable buttons
      initializeBtn.disabled = false;
      terminateBtn.disabled = true;
      processBtn.disabled = true;
      executeToolBtn.disabled = true;

      addNotification('Client terminated successfully.', 'success');
    } else {
      statusText.textContent = 'Error';
      addNotification(`Termination failed: ${result.error}`, 'error');
      terminateBtn.disabled = false;
    }
  } catch (error) {
    statusText.textContent = 'Error';
    addNotification(`Termination error: ${error.message}`, 'error');
    terminateBtn.disabled = false;
  }
}

// Process an LLM prompt
async function processPrompt() {
  try {
    const prompt = promptInput.value.trim();

    if (!prompt) {
      addNotification('Please enter a prompt.', 'error');
      return;
    }

    // Disable process button
    processBtn.disabled = true;

    // Call process endpoint
    const response = await fetch('/process', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ prompt })
    });

    const result = await response.json();

    // Display result
    if (result.status === 'success') {
      outputDisplay.innerHTML += `<div class="prompt"><strong>Prompt:</strong> ${prompt}</div>`;
      outputDisplay.innerHTML += `<div class="response"><strong>Response:</strong> ${result.data.response}</div>`;

      // Clear prompt input
      promptInput.value = '';

      addNotification('Prompt processed successfully.', 'success');
    } else {
      addNotification(`Processing failed: ${result.error || 'Unknown error'}`, 'error');
    }

    // Enable process button
    processBtn.disabled = false;

    // Scroll to bottom of output
    outputDisplay.scrollTop = outputDisplay.scrollHeight;
  } catch (error) {
    addNotification(`Processing error: ${error.message}`, 'error');
    processBtn.disabled = false;
  }
}

// Execute a tool
async function executeTool() {
  try {
    const tool = toolSelect.value;
    const operation = operationSelect.value;

    // Collect parameters
    const params = {};
    const paramFields = document.querySelectorAll('.param-field');

    paramFields.forEach(field => {
      const paramName = field.getAttribute('data-param');
      let value = field.value;

      // Convert number inputs to actual numbers
      if (field.type === 'number') {
        value = Number(value);
      }

      // Try to parse JSON for textarea inputs (for json_to_csv)
      if (field.tagName === 'TEXTAREA' && operation === 'json_to_csv') {
        try {
          value = JSON.parse(value);
        } catch (e) {
          throw new Error('Invalid JSON data');
        }
      }

      params[paramName] = value;
    });

    // Disable execute button
    executeToolBtn.disabled = true;

    // Call tools endpoint
    const response = await fetch('/tools', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        tool,
        operation,
        params
      })
    });

    const result = await response.json();

    // Display result
    if (result.status === 'success') {
      const resultData = JSON.stringify(result.data.result, null, 2);
      toolResult.innerHTML = `<pre>${resultData}</pre>`;

      addNotification(`Tool ${tool}.${operation} executed successfully.`, 'success');
    } else {
      toolResult.innerHTML = `<div class="error">Error: ${result.error || 'Unknown error'}</div>`;
      addNotification(`Tool execution failed: ${result.error || 'Unknown error'}`, 'error');
    }

    // Enable execute button
    executeToolBtn.disabled = false;
  } catch (error) {
    toolResult.innerHTML = `<div class="error">Error: ${error.message}</div>`;
    addNotification(`Tool execution error: ${error.message}`, 'error');
    executeToolBtn.disabled = false;
  }
}

// Add a notification
function addNotification(message, type = 'info') {
  const notificationElement = document.createElement('div');
  notificationElement.className = `notification notification-${type}`;

  const timeElement = document.createElement('div');
  timeElement.className = 'notification-time';
  timeElement.textContent = new Date().toLocaleTimeString();

  const messageElement = document.createElement('div');
  messageElement.textContent = message;

  notificationElement.appendChild(timeElement);
  notificationElement.appendChild(messageElement);

  notificationsDisplay.appendChild(notificationElement);

  // Scroll to bottom of notifications
  notificationsDisplay.scrollTop = notificationsDisplay.scrollHeight;
}

// Update operation select based on selected tool
function updateOperations() {
  const tool = toolSelect.value;
  const operations = tools[tool].operations;

  // Clear operations
  operationSelect.innerHTML = '';

  // Add operations
  operations.forEach(operation => {
    const option = document.createElement('option');
    option.value = operation;
    option.textContent = operation;
    operationSelect.appendChild(option);
  });

  // Update parameters
  updateParameters();
}

// Update parameters based on selected tool and operation
function updateParameters() {
  const tool = toolSelect.value;
  const operation = operationSelect.value;
  const params = tools[tool].params[operation];

  // Clear parameters
  paramsContainer.innerHTML = '';

  // Add parameter fields
  params.forEach(param => {
    const formGroup = document.createElement('div');
    formGroup.className = 'form-group';

    const label = document.createElement('label');
    label.textContent = param.label;

    let input;

    if (param.type === 'textarea') {
      input = document.createElement('textarea');
      input.rows = 5;
    } else {
      input = document.createElement('input');
      input.type = param.type;
    }

    input.className = 'param-field';
    input.setAttribute('data-param', param.name);

    formGroup.appendChild(label);
    formGroup.appendChild(input);

    paramsContainer.appendChild(formGroup);
  });
}

// Initialize tool operations
updateOperations();

// Event listeners
initializeBtn.addEventListener('click', initializeClient);
terminateBtn.addEventListener('click', terminateClient);
processBtn.addEventListener('click', processPrompt);
executeToolBtn.addEventListener('click', executeTool);
toolSelect.addEventListener('change', updateOperations);
operationSelect.addEventListener('change', updateParameters);

// Add notification on load
addNotification('MCP Client Interface loaded.');
