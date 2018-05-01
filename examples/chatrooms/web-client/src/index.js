/*
    Application Entry Point 
*/
import React from 'react';
import {render} from 'react-dom';
import { createStore, compose, applyMiddleware } from 'redux';
import reduxThunk from 'redux-thunk';
import { Provider } from 'react-redux';
import createHistory from 'history/createBrowserHistory';
import { routerMiddleware } from 'react-router-redux';

import './tbone.config';


import rootReducer from './reducers';
import App from './components/app'

export const history = createHistory();

function configureStore(initialState){
    const store = createStore(
        rootReducer,
        initialState,
        compose(
            applyMiddleware(reduxThunk, routerMiddleware(history)),
            window.__REDUX_DEVTOOLS_EXTENSION__ && window.__REDUX_DEVTOOLS_EXTENSION__()
        )
    );
    if (module.hot) {
        // Enable Webpack hot module replacement for reducers
        module.hot.accept('./reducers', () => {
            const nextRootReducer = require('./reducers').default;
            store.replaceReducer(nextRootReducer);
        });
    }
    return store;
}


render(
    <Provider store={configureStore()}>
        <App/>
    </Provider>
    , document.getElementById('app')
);