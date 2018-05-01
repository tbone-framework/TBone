import { combineReducers } from 'redux';
import { actionTypes } from '../actions/messages';

/*
Convert array of server objects (with _id) to  a dict-like object
*/
const arrayToObject = (array) =>
    array.reduce((obj, item) => {
        obj[item._id] = item
        return obj
    }, {})


const initialState = {
    entities:{},
    meta: null,
    timeline: {
        buckets: {},
        active: null
    },
    unread: [],
    loading: false,
    sending: false,
}




export default function(state=initialState, action){
    switch(action.type){
        case actionTypes.FetchMessagesRequest:
        return{
            ...state,
            loading: true
        }
        case actionTypes.FetchMessagesSuccess:
            // map new incoming messages by converting the creation date to real Date object
            const incomingItems = action.payload.objects.map(msg => ({...msg, created: new Date(msg.created)}));
            // filter the incoming messages to process only new ones, skipping existing ones
            const newItems = incomingItems.filter(item => !Object.keys(state.entities).includes(item._id));
            // return a new state if there are new messages
            if(newItems.length){
                let newState = {
                    ...state,
                    meta: action.payload.meta,
                    entities:{
                        ...state.entities,
                        ...arrayToObject(newItems)                        
                    },
                    unread: [...state.unread, ...newItems.map(msg => msg._id)],
                    loading: false
                }
                return newState;
            }
            return { ...state, loading: false }
        case actionTypes.FetchMessagesError:
            debugger;
            return state;

        case actionTypes.sendMessageRequest:
            return {...state, sending: true};

        case actionTypes.sendMessageSuccess:
            return {
                ...state,
                entities:{
                    ...state.entities,
                    [action.payload._id]: action.payload                       
                },
                unread:[...state.unread, action.payload._id],
                sending: false
            };

        case actionTypes.sendMessageError:
            debugger;
            return {...state, sending: false};

    }
}



// export default combineReducers({
//     meta, entities, timeline, loading
// });