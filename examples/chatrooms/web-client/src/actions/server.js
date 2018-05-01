

export const actionTypes = {
    ConnectionRequest: 'CONNECTION_REQUEST',
    ConnectionSuccess: 'CONNECTION_SUCCESS',
    ConnectionError: 'CONNECTION_ERROR',
}


export function requestConnection(){
    return{
        type: actionTypes.ConnectionRequest
    }
}

export function connectionSuccess(){
    return{
        type: actionTypes.ConnectionSuccess
    }
}
