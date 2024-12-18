document.addEventListener("DOMContentLoaded", function () {
    const kilometerField = document.querySelector('#id_kilometer');
    const branchSelect = document.querySelector('#id_branch');
    const destinationPinCodeField = document.querySelector('#id_pin_code'); // Target the correct field

    console.log('Kilometer Field:', kilometerField);
    console.log('Branch Select Field:', branchSelect);
    console.log('Destination Pin Code Field:', destinationPinCodeField);
    console.log('Initial Destination Pin Code Value:', destinationPinCodeField ? destinationPinCodeField.value : 'No Field Found');

    if (kilometerField && branchSelect && destinationPinCodeField) {

        const checkButton = document.createElement('button');
        checkButton.innerText = 'Check';
        checkButton.type = 'button';
        checkButton.classList.add('button', 'default');
        checkButton.style.marginLeft = '10px';

        destinationPinCodeField.parentNode.insertBefore(checkButton, destinationPinCodeField.nextSibling);


        const locationDropdown = document.createElement('select');
        locationDropdown.id = 'locationDropdown';
        locationDropdown.classList.add('button', 'default');
        locationDropdown.style.marginLeft = '10px';
        locationDropdown.style.display = 'none'; // Initially hidden
        checkButton.parentNode.insertBefore(locationDropdown, checkButton.nextSibling);


        // Create Loading Spinner
        const loadingSpinner = document.createElement('div');
        loadingSpinner.id = 'loadingSpinner';
        loadingSpinner.classList.add('spinner');
        loadingSpinner.style.display = 'none'; // Initially hidden
        checkButton.parentNode.insertBefore(loadingSpinner, locationDropdown.nextSibling);



        const refreshButton = document.createElement('button');
        refreshButton.innerText = 'Calculate';
        refreshButton.type = 'button';
        refreshButton.classList.add('button', 'default');
        refreshButton.style.marginLeft = '10px';

        kilometerField.parentNode.insertBefore(refreshButton, kilometerField.nextSibling);


        checkButton.addEventListener('click', function () {
            const destinationPinCode = destinationPinCodeField.value;
            console.log("Reached to check statement: " + destinationPinCode);

            // Clear previous options and hide dropdown
            const dropdown = document.querySelector('#locationDropdown');
            dropdown.innerHTML = ''; // Clear previous options
            dropdown.style.display = 'none'; // Hide dropdown initially


            loadingSpinner.style.display = 'inline';

            fetch(`https://india-pincode-with-latitude-and-longitude.p.rapidapi.com/api/v1/pincode/${destinationPinCode}`, {
                method: 'GET',
                headers: {
                    'x-rapidapi-host': 'india-pincode-with-latitude-and-longitude.p.rapidapi.com',
                    'x-rapidapi-key': '81bc83f006mshfcaf5ba098b22b7p102e43jsn5ce3f81cd0d3'
                }
            })
                .then(response => {
                    if (!response.ok) {
                        throw new Error(`HTTP error! status: ${response.status}`);
                    }
                    return response.json();
                })
                .then(data => {
                    console.log("API response:", data);

                    if (Array.isArray(data) && data.length > 0) {
                        data.forEach(location => {
                            const option = document.createElement('option');
                            option.textContent = `${location.area}`;
                            option.value = `${location.lat},${location.lng}`;
                            dropdown.appendChild(option);
                        });

                        dropdown.style.display = 'inline'; // Show dropdown after updating
                    } else {
                        dropdown.style.display = 'none'; // Hide dropdown if no results
                    }
                })
                .catch(error => {
                    console.log('Fetch Error:', error);
                    dropdown.style.display = 'none'; // Hide dropdown on fetch error
                })
                .finally(() => {
                    // Hide loading spinner
                    loadingSpinner.style.display = 'none';
                });
        });

        //     // Make API call with the destinationPinCode
        //     fetch(`https://api.worldpostallocations.com/pincode?postalcode=${destinationPinCode}&countrycode=IN`)
        //         .then(response => {
        //             if (!response.ok) {
        //                 throw new Error(`HTTP error! status: ${response.status}`);
        //             }
        //             return response.json();
        //         })
        //         .then(data => {
        //             console.log("API response:", data);

        //             if (data.status && data.result) {
        //                 if (data.result.length > 0) {
        //                     data.result.forEach(location => {
        //                         const option = document.createElement('option');
        //                         option.textContent = location.postalLocation;
        //                         option.value = `${location.latitude},${location.longitude}`;
        //                         dropdown.appendChild(option);
        //                     });

        //                     dropdown.style.display = 'inline'; // Show dropdown after updating
        //                 } else {
        //                     dropdown.style.display = 'none'; // Hide dropdown if no results
        //                 }
        //             } else if (data.error) {
        //                 console.log('Error:', data.error);
        //                 dropdown.style.display = 'none'; // Hide dropdown on error
        //             }
        //         })
        //         .catch(error => {
        //             console.log('Fetch Error:', error);
        //             dropdown.style.display = 'none'; // Hide dropdown on fetch error
        //         })
        //         .finally(() => {
        //             // Hide loading spinner
        //             loadingSpinner.style.display = 'none';
        //         });
        // });






        refreshButton.addEventListener('click', function () {
            const selectedBranchId = branchSelect.value;
            const destinationPinCode = destinationPinCodeField.value;
            const selectedPlace = locationDropdown.value.split(',');

            console.log('Selected Branch ID:', selectedBranchId);
            console.log('Destination Pin Code:', destinationPinCode);
            console.log('selected Place:', selectedPlace);

            if (selectedBranchId && selectedPlace.length === 2) {
                fetch(`/destinations/get-branch-pincode/${selectedBranchId}/`)
                    .then(response => {
                        if (!response.ok) {
                            throw new Error(`HTTP error! status: ${response.status}`);
                        }
                        return response.json();
                    })
                    .then(data => {
                        console.log("new log statemetn" + data.longitude);

                        if (data.latitude !== undefined && data.longitude !== undefined) {

                            const branchLat = data.latitude;
                            const branchLon = data.longitude;
                            const placeLat = parseFloat(selectedPlace[0]);
                            const placeLon = parseFloat(selectedPlace[1]);

                            // Calculate the distance
                            const distance = calculateDistance(branchLat, branchLon, placeLat, placeLon);
                            kilometerField.value = distance.toFixed(2);

                            console.log('Branch latitude:', data.latitude);
                            console.log('Branch longitude:', data.longitude);
                            console.log('Destination Pin Code after fetch:', destinationPinCode);
                            console.log('Distance between branch and selected place:', distance.toFixed(2), 'km');

                        } else if (data.error) {
                            console.log('Error:', data.error);
                        }
                    })
                    .catch(error => console.log('Fetch Error:', error));
            } else {
                console.log('Branch ID not selected');
            }
        });
    } else {
        console.log('Kilometer field, Branch select field, or Destination pin code field not found');
    }
});



function calculateDistance(lat1, lon1, lat2, lon2) {

    console.log("kkjhkdgskljskldjkl");

    console.log(lat1, lon1, lat2, lon2);

    const R = 6371; // Radius of the Earth in kilometers
    const dLat = (lat2 - lat1) * (Math.PI / 180);
    const dLon = (lon2 - lon1) * (Math.PI / 180);

    const a = Math.sin(dLat / 2) * Math.sin(dLat / 2) +
        Math.cos(lat1 * (Math.PI / 180)) * Math.cos(lat2 * (Math.PI / 180)) *
        Math.sin(dLon / 2) * Math.sin(dLon / 2);

    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
    const distance = R * c; // Distance in kilometers

    return distance;
}