// Initialize an empty dictionary to store data
let dataDictionary = {};

// Function to add data
function addData() {
  // Prompt the user to enter a key and a value
  const key = prompt('Enter a key:');
  const value = prompt('Enter a value:');

  if (key !== null && key !== '' && value !== null && value !== '') {
    // Add the data to the dictionary
    dataDictionary[key] = value;

    // Store the updated dictionary as a JSON string
    localStorage.setItem('dataDictionary', JSON.stringify(dataDictionary));

    // Display the updated data
    displayData();
  }
}

// Function to remove data
function removeData(key) {
  // Remove the data with the specified key from the dictionary
  delete dataDictionary[key];

  // Store the updated dictionary as a JSON string
  localStorage.setItem('dataDictionary', JSON.stringify(dataDictionary));

  // Display the updated data
  displayData();
}

// Function to display the data
function displayData() {
  const dataListElement = document.getElementById('dataList');
  dataListElement.innerHTML = '';

  // Loop through the dictionary and create list items
  for (const key in dataDictionary) {
    const liElement = document.createElement('li');
    liElement.textContent = `${key}: ${dataDictionary[key]}`;

    // Create a button to remove the data
    const removeButton = document.createElement('button');
    removeButton.textContent = 'Remove';
    removeButton.addEventListener('click', () => removeData(key));

    liElement.appendChild(removeButton);
    dataListElement.appendChild(liElement);
  }
}

// Retrieve the stored data dictionary from localStorage
const storedData = localStorage.getItem('dataDictionary');
if (storedData) {
  dataDictionary = JSON.parse(storedData);
  displayData();
}

// Add an event listener to the button
document.getElementById('addDataButton').addEventListener('click', addData);
