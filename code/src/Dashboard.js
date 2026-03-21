import React, { Component } from 'react'
import { Container, Row, Col, Alert } from 'react-bootstrap'
import { Navigate } from 'react-router-dom'
import { Auth } from './utils/Auth'
import styled from 'styled-components'

const Styles = styled.div`
    .padding-bottom {
        padding-bottom: 16px;
    }

    .center {
        width: fit-content;
        text-align: center;
        margin: 1em auto;
        display: table;
    }
`

export class Dashboard extends Component {

    constructor(props) {
        super(props);
        this.auth = new Auth()
        this.state = { "profile": this.auth.getUserProfile() }
    }

    render() {
        if (this.props.authenticated === false)
            return <Navigate to='/login' />
        return (
            <Styles>
                <Container>
                    <Row className="padding-bottom">
                        <Col lg={{ span: 12 }} className="center">
                            <h1>Hello { this.state.profile.first_name } !</h1>
                            <p>
                                You are on your dashboard page.
                            </p>
                            <Alert variant={"dark"}>
                                You are logged in as <b>{ this.state.profile.username }</b>
                            </Alert>
                        </Col>
                    </Row>
                </Container>
            </Styles>
        )
    }

    componentDidMount() {
        document.title = "Dashboard - Hello Roberto";
    }

}

export default Dashboard;
