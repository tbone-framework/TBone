import configureStore from 'redux-mock-store'
import thunk from 'redux-thunk'

import * as actions from './channels';


const middlewares = [thunk] // add your middlewares like `redux-thunk`
const mockStore = configureStore(middlewares)


describe('async actions', () => {
    it('should execute fetchChannels', ()=>{

        const store = mockStore({});

        // return store.dispatch(actions.fetchRooms()).then(()=>{
        //     const actions = store.getActions();
        //     expect(actions[0]).toEqual(success());
        // });


    })
})