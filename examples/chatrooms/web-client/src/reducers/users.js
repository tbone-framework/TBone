import { actionTypes } from '../actions/users';

const initialState =  {
    items: [],
    thisUserId: null
};

const arrayToObject = (array) =>
   array.reduce((obj, item) => {
     obj[item._id] = item
     return obj
   }, {})

export default function(state=initialState, action) {
    switch(action.type){
        case actionTypes.FetchUsersSuccess:
            const items = state.items;
            const newItems = arrayToObject(action.payload.objects); 
            return {
                ...state,
                 items: {
                    ...items,
                    ...newItems
                 }
            }
        case actionTypes.FetchUsersError:
            return state;
        default:
            return state;
    }
}

