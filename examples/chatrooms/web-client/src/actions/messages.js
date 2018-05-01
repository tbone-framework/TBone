import TBone from '@475cumulus/tbone';

export const actionTypes = {
    FetchMessagesRequest: 'FETCH_CHANNEL_MESSAGES_REQUEST',
    FetchMessagesSuccess: 'FETCH_CHANNEL_MESSAGES_SUCCESS',
    FetchMessagesError: 'FETCH_CHANNEL_MESSAGES_ERROR',

    addMessage: 'ADD_MESSAGE',

    sendMessageRequest: 'SEND_MESSAGE_REQUEST',
    sendMessageSuccess: 'SEND_MESSAGE_SUCCESS',
    sendMessageError: 'SEND_MESSAGE_ERROR',
}

const API_CHANNELS_URL = '/api/team/channel/';

export function fetchMessages(channel, before){
    return dispatch =>{ 
        dispatch({ // create action that fetching of messages has started
            type: actionTypes.FetchMessagesRequest,
            channel_id: channel._id
        }); 
        TBone.resource(`${API_CHANNELS_URL}${channel.name}/entry/`).get({limit:0}).then((response) => dispatch({
            type: actionTypes.FetchMessagesSuccess,
            channel_id: channel._id,
            payload: response.payload
        })).catch((error) => dispatch({
            type: actionTypes.FetchMessagesError,
            channel_id: channel._id,
            payload: error
        }));
    }
}

export function sendMessage(channel, message){
    return (dispatch) => {
        dispatch({
            type: actionTypes.sendMessageRequest,
            channel,
            message
        }); 
        TBone.resource(`${API_CHANNELS_URL}${channel.name}/entry/`).post({},{
            text: message
        }).then((response) => dispatch({
            type: actionTypes.sendMessageSuccess,
            channel_id: channel._id,
            payload: response.payload
        })).catch((error) => dispatch({
            type: actionTypes.sendMessageError,
            channel_id: channel._id,
            payload: error
        }));
    }   
}

