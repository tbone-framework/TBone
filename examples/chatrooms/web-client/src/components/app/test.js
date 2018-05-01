import React from 'react';
import { mount } from 'enzyme';
import App from '.';


describe('App', () =>{

    let app = mount(<App />);

    it('renders', ()=>{
        // console.log(app.debug());
    });
});