function get_therapists(id) {
    var therapists = [];
    var data = {};

    if (id) {
        data = {
            id: id
        };
    }
    
    $.ajax({
        url: '/api/therapists',
        type: 'GET',
        async: false,
        data: data,
        success: function(response) {
            therapists = response;
        },
        error: function(error) {
            console.log(error);
            alert('Error getting therapists; check console');
        }
    });

    return therapists;
}

function search_therapists(query) {
    var therapists = [];
    
    $.ajax({
        url: '/api/search',
        type: 'GET',
        async: false,
        data: {
            q: query
        },
        success: function(response) {
            therapists = response;
        },
        error: function(error) {
            console.log(error);
            alert('Error getting therapists; check console');
        }
    });

    return therapists;
    
}

function user_signup(data) {
    var response = {};
    
    $.ajax({
        url: '/api/signup',
        type: 'POST',
        async: false,
        data: data,
        success: function(res) {
            response = res;
        },
        error: function(error) {
            response = error;
        }
    });

    return response;
}

function user_login(data) {
    var response = {};
    
    $.ajax({
        url: '/api/login',
        type: 'POST',
        async: false,
        data: data,
        success: function(res) {
            response = res;
        },
        error: function(error) {
            response = error;
        }
    });

    return response;
}

function get_user() {
    var response = {};
    
    $.ajax({
        url: '/api/user',
        type: 'GET',
        async: false,
        success: function(res) {
            response = res;
        },
        error: function(error) {
            response = error;
        }
    });

    return response;
}

function get_user_profile() {
    var response = {};
    
    $.ajax({
        url: '/api/profile',
        type: 'GET',
        async: false,
        success: function(res) {
            response = res;
        },
        error: function(error) {
            response = error;
        }
    });

    return response;
}

function edit_user_profile(data) {
    // data is a FormData object
    var response = {};
    
    $.ajax({
        url: '/api/profile',
        type: 'POST',
        async: false,
        data: data,
        contentType: false, // No content type specified (automatically set by FormData)
        processData: false, // Don't process data (FormData does that for us)
        success: function(res) {
            response = res;
        },
        error: function(error) {
            response = error;
        }
    });

    return response;
}

function schedule_appointment(data) {
    var response = {};
    
    $.ajax({
        url: '/api/schedule_appointment',
        type: 'POST',
        async: false,
        data: data,
        success: function(res) {
            response = res;
        },
        error: function(error) {
            response = error;
        }
    });

    return response;
}
