function writeResponse(objectId, data) {
    let text = '';
    for (let key in data) {
        text += key + ': ' + data[key] + '<br/>';
    }
    $(objectId).html(text);
}

function sendAuthenticatedRequest(method, rid, token, objectId, body=null) {
    let headers = new Headers();
    if (rid && token) {
        headers.append(
            'Authorization',
            'Basic ' + btoa(rid + ":" + token)
        );
    }
    let url = 'http://127.0.0.1:8000/api/v1/registrations/' + rid + '/';
    if (body) {
        body = JSON.stringify(body);
    } else {
        body = JSON.stringify({});
    }
    fetch(url, {
        method: method,
        headers: headers,
        body: body
    }).then(function(response) {
        if (!response.ok) {
            throw Error(response.statusText);
        }
        return response.json();
    }).then(function(data) {
        writeResponse(objectId, data);
    }).catch(function(detail) {
        $(objectId).html(detail);
    });
}

function getRequestResponse() {
    let values = {};
    $.each($('#viewRequestForm').serializeArray(), function(i, field) {
        values[field.name] = field.value;
    });
    sendAuthenticatedRequest('GET', values['rid'], values['token'],
        '#viewRequestResponse');
}
$("#viewRequestForm").submit(function(e) {
    e.preventDefault();
    getRequestResponse();
});

function createRegistration() {
    let values = {};
    $.each($('#createRequestForm').serializeArray(), function(i, field) {
        values[field.name] = field.value;
    });
    let url = 'http://127.0.0.1:8000/api/v1/registrations/';
    let body;
    if (values['email']) {
        body = JSON.stringify(values);
    } else {
        body = JSON.stringify({});
    }
    fetch(url, {
        method: 'POST',
        body: body,
    }).then(function(response) {
        if (!response.ok) {
            throw Error(response.statusText);
        }
        return response.json();
    }).then(function(data) {
        writeResponse('#createRequestResponse', data);
    }).catch(function(detail) {
        $('#createRequestResponse').html(detail);
    });
}
$("#createRequestForm").submit(function(e) {
    e.preventDefault();
    createRegistration();
});

function approveRejectRequest() {
    let values = {};
    $.each($('#approveRejectForm').serializeArray(), function(i, field) {
        values[field.name] = field.value;
    });
    sendAuthenticatedRequest('PUT', values['rid'], values['token'],
        '#approveRejectResponse', values);
}
$("#approveRejectForm").submit(function(e) {
    e.preventDefault();
    approveRejectRequest();
});

function createAccountRequest() {
    let values = {};
    $.each($('#createAccountForm').serializeArray(), function(i, field) {
        values[field.name] = field.value;
    });
    sendAuthenticatedRequest('PATCH', values['rid'], values['token'],
        '#createAccountResponse', values);
}
$("#createAccountForm").submit(function(e) {
    e.preventDefault();
    createAccountRequest();
});

function deleteAccountRequest() {
    let values = {};
    $.each($('#deleteRequestForm').serializeArray(), function(i, field) {
        values[field.name] = field.value;
    });
    sendAuthenticatedRequest('DELETE', values['rid'], values['token'],
        '#deleteRequestResponse');
}
$("#deleteRequestForm").submit(function(e) {
    e.preventDefault();
    deleteAccountRequest();
});
