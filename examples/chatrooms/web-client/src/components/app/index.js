import React, { Component } from 'react';
import { ConnectedRouter } from 'react-router-redux';
import { Route, Redirect } from 'react-router-dom';
import createHistory from 'history/createBrowserHistory'
import 'semantic-ui-css/semantic.min.css';

import Layout from '../layout';


const PrivateRoute = ({component: Component, authenticated, ...props}) => {
    return (
        <Route
            {...props}
            render={(props) => authenticated === true
                ? <Component {...props} />
                : <Redirect to={{pathname: '/login', state: {from: props.location}}} />}
        />
    );
};

const PublicRoute = ({component: Component, authenticated, ...props}) => {
    return (
        <Route
            {...props}
            render={(props) => authenticated === false
                ? <Component {...props} />
                : <Redirect to='/' />}
        />
    );
};


class App extends Component {
    render() {
        return (
            <ConnectedRouter history={createHistory()}>
                    <Route
                        authenticated={this.props.authenticated }
                        path='/'
                        component={ Layout }
                    />
            </ConnectedRouter>
        );
    }
}



export default App;