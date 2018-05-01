import TBone from '@475cumulus/tbone';

export const actionTypes = {
    FetchUsersSuccess: 'FETCH_USER_SUCCESS',
    FetchUsersError: 'FETCH_USER_ERROR',
}

const API_USERS_URL = '/api/team/user/';


export function fetchUsers(user){
    return function (dispatch){ 
        TBone.resource(API_USERS_URL).get().then((response) => dispatch({
            type: actionTypes.FetchUsersSuccess,
            payload: response.payload
        })).catch((error) => dispatch({
            type: actionTypes.FetchUsersError,
            payload: error
        }));
    }
}