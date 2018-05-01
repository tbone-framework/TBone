
import { combineReducers } from 'redux';
import ChannelsReducer from './channels';
import UsersReducer from './users';

const rootReducer = combineReducers({
  channels: ChannelsReducer,
  users: UsersReducer
});

export default rootReducer;

