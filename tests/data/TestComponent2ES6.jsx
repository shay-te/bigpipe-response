class TestComponent2ES6 extends React.Component {
  constructor() {
    super();
    this.state = {color: "ow"};
  }

    // Set default props
  static defaultProps = {
    size: 555,
  }

  render() {
    return (<div>
        <h2>Hi, I am a Component!</h2>
        <div>state color 2: {this.state.color}</div>
        <div>sprops size 2: {this.props.size}</div>
    </div>);
  }
}

export default TestComponent2ES6;