function initAutocomplete() {
    var input = document.getElementById('id_location');
    var autocomplete = new google.maps.places.Autocomplete(input);

    autocomplete.addListener('place_changed', function () {
        var place = autocomplete.getPlace();
        if (!place.geometry) {
            return;
        }
        document.getElementById('id_latitude').value = place.geometry.location.lat();
        document.getElementById('id_longitude').value = place.geometry.location.lng();
        document.getElementById('id_address').value = place.formatted_address;
    });
}
