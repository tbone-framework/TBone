import TBone from '@475cumulus/tbone';
import { fetchMessages } from './messages';

export const actionTypes = {
    SelectChannel: 'SELECT_CHANNEL',
    UnSelectChannel: 'UNSELECT_CHANNEL',

    FetchChannelsRequest: 'FETCH_CHANNELS_REQUEST',
    FetchChannelsSuccess: 'FETCH_CHANNELS_SUCCESS',
    FetchChannelsError: 'FETCH_CHANNELS_ERROR',
}

const API_CHANNELS_URL = '/api/team/channel/';


export function selectChannel(channel){
    return (dispatch) => {
        // we started listening to childs added to the messages of the selected part
        // Firebase.database().ref(`parts/${part.id}/messages`).on('child_added', snapshot => {
        //     const msg = snapshot.val();
        //     msg.id = snapshot.key;
        //     dispatch(addMessage(part, msg));
        // });
        dispatch(fetchMessages(channel));
        dispatch({
            type: actionTypes.SelectChannel,
            channel: channel._id
        });        
    }
}

export function fetchChannels(user){
    return dispatch => {
        dispatch({
            type: actionTypes.FetchChannelsRequest
        });         
        TBone.resource(API_CHANNELS_URL).get().then((response) => dispatch({
            type: actionTypes.FetchChannelsSuccess,
            payload: response.payload
        })).catch((error) => dispatch({
            type: actionTypes.FetchChannelsError,
            payload: error
        }));
    }
}


export function addMessage(channel, msg){
    return{
        type: actionTypes.AddMessage,
        channel: channel,
        message: msg
    }
}

export function sendMessage(channel, msg){
    return (dispatch) => {
        // var new_message = {
        //     message: {
        //         type: 'text',
        //         message: msg.message,
        //     },
        //     timestamp: new Date().toISOString(),
        //     uid: Firebase.auth().currentUser.uid

        // }
        // const ref = Firebase.database().ref(`parts/${part.id}/messages`).push(); 
        // new_message.id = ref.key;
        // ref.set(new_message);
    }   
}

