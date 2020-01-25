import TestComponent2ES6 from './TestComponent2ES6.jsx';


class TestComponentES6 extends React.Component {
  constructor() {
    super();
    this.state = {color: "red"};
  }

    // Set default props
  static defaultProps = {
    size: 50,
  }

  render() {
    return (<div>
        <h2>Hi, I am a Component!</h2>
        <div>state color: {this.state.color}</div>
        <div>sprops size: {this.props.size}</div>
        <TestComponent2ES6 size={666}></TestComponent2ES6>
    </div>);
  }
}

export default TestComponentES6;