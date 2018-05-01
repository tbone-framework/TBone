import update from 'immutability-helper';

import { actionTypes } from '../actions/channels';
import { actionTypes as msgActionTypes } from '../actions/messages';
import messageReducer from './messages';

const CHANNEL_PUBLIC = 10;
const CHANNEL_PRIVATE = 20;

const initialState =  {
    entities: {},
    meta: null,
    rooms: [],
    direct: [],
    selected: null,
    loading: false
};

const arrayToObject = (array) =>
    array.reduce((obj, item) => {
        obj[item._id] = item
        return obj
    }, {})



export default function(state=initialState, action) {
    switch(action.type){
        case actionTypes.SelectChannel:
            return {
                ...state,
                selected: action.channel
            }
        case actionTypes.FetchChannelsRequest:
            return {
                ...state,
                loading: true
            }
        case actionTypes.FetchChannelsSuccess:
            const newEntities = arrayToObject(action.payload.objects);
            return {
                ...state,
                meta: action.payload.meta,
                entities: {
                    ...state.entities,
                    ...newEntities
                },
                rooms: [
                    ...state.rooms,
                    ...action.payload.objects.filter(channel => channel.access <= 20).map(channel => channel._id)
                ],
                direct: [
                    ...state.direct,
                    ...action.payload.objects.filter(channel => channel.access > 20)
                ],
                loading: false
            }
        case actionTypes.FetchChannelsError:
            return {
                ...state,
                loading: false
            };

        case msgActionTypes.FetchMessagesRequest:
        case msgActionTypes.FetchMessagesSuccess:
        case msgActionTypes.FetchMessagesError:
        case msgActionTypes.addMessage:
        case msgActionTypes.sendMessageRequest:
        case msgActionTypes.sendMessageSuccess:
        case msgActionTypes.sendMessageError:
            // get the channel we're updating
            const channel_id = action.channel_id;
            let mutatedChannel = {...state.entities[channel_id] };
            // call the nested message reducer
            mutatedChannel.messages = messageReducer(mutatedChannel.messages , action);
            return{
                ...state,
                entities:{
                    ...state.entities,
                    [channel_id]: mutatedChannel
                }
            }

        default:
            return state;

    }
}