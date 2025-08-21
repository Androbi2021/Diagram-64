import { useState } from 'react';
import axios from 'axios';
import {
  Layout,
  Form,
  Input,
  InputNumber,
  Button,
  ColorPicker,
  Spin,
  Row,
  Col,
  Card,
  Typography,
  notification,
  Checkbox,
} from 'antd';

const { Header, Content } = Layout;
const { Title } = Typography;
const { TextArea } = Input;

function App() {
  const [loading, setLoading] = useState(false);
  const [form] = Form.useForm();

  const handleGeneratePdf = async (values) => {
    const lines = values.fens.split('\n').filter((line) => line.trim() !== '');
    if (lines.length === 0) {
      notification.error({
        message: 'Validation Error',
        description: 'Please enter at least one FEN string.',
      });
      return;
    }

    const fenData = lines.map(line => {
      const parts = line.split(/ \/\/ (.*)/s);
      return {
        fen: parts[0],
        description: parts[1] || '',
      };
    });

    setLoading(true);

    const getColorString = (colorValue) => {
      if (typeof colorValue === 'object' && colorValue !== null && typeof colorValue.toHexString === 'function') {
        return colorValue.toHexString();
      }
      return colorValue;
    };

    const payload = {
      fens: fenData,
      diagrams_per_page: values.diagramsPerPage,
      padding: {
        top: values.padding,
        bottom: values.padding,
        left: values.padding,
        right: values.padding,
      },
      board_colors: {
        light_squares: getColorString(values.lightSquares),
        dark_squares: getColorString(values.darkSquares),
        border_color: getColorString(values.borderColor),
      },
      columns_for_diagrams_per_page: {
        single_column: values.singleColumn,
        two_column_max: values.twoColumnMax,
      },
      title: values.title,
      show_turn_indicator: values.showTurnIndicator,
      show_page_numbers: values.showPageNumbers,
    };

    try {
      const response = await axios.post('/api/generate-pdf/', payload, {
        responseType: 'blob',
      });

      const file = new Blob([response.data], { type: 'application/pdf' });
      const fileURL = URL.createObjectURL(file);

      const link = document.createElement('a');
      link.href = fileURL;
      link.setAttribute('download', 'chess_diagrams.pdf');
      document.body.appendChild(link);
      link.click();

      link.parentNode.removeChild(link);
      URL.revokeObjectURL(fileURL);

      notification.success({
        message: 'PDF Generated',
        description: 'Your chess diagram PDF has been successfully generated.',
      });
    } catch (err) {
      let errorMessage = 'An unexpected error occurred.';
      if (err.response?.data?.error) {
        errorMessage = err.response.data.error;
      } else if (err.message) {
        errorMessage = err.message;
      }

      notification.error({
        message: 'Error Generating PDF',
        description: errorMessage,
        duration: 10,
      });

      console.error('Full error object:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Layout style={{ minHeight: '100vh', background: '#f0f2f5' }}>
      <Header style={{ background: '#001529', padding: '0 24px' }}>
        <Title level={2} style={{ color: 'white', lineHeight: '64px', margin: 0 }}>
          Chess Diagram PDF Generator
        </Title>
      </Header>
      <Content style={{ padding: '24px' }}>
        <Row justify="center">
          <Col xs={24} sm={20} md={20} lg={20} xl={20}>
            <Card>
              <Spin spinning={loading} tip="Generating PDF...">
                <Form
                  form={form}
                  layout="vertical"
                  onFinish={handleGeneratePdf}
                  initialValues={{
                    title: '',
                    fens: '',
                    diagramsPerPage: 6,
                    padding: 2.5,
                    lightSquares: '#f0d9b5',
                    darkSquares: '#b58863',
                    borderColor: '#ffffffff',
                    singleColumn: 1,
                    twoColumnMax: 8,
                    showTurnIndicator: true,
                    showPageNumbers: false,
                  }}
                >
                  <Form.Item
                    name="title"
                    label="Enter the title of your PDF (facultative):"
                    rules={[{ required: false}]}
                  >
                    <TextArea
                      rows={1}
                      placeholder="My PDF title"
                      style={{ fontFamily: "Arial" }}
                    />
                  </Form.Item>

                  <Form.Item
                    name="fens"
                    label="Enter FEN and description (one per line):"
                    rules={[{ required: true, message: 'Please input at least one FEN string!' }]}
                  >
                    <TextArea
                      rows={10}
                      placeholder="e.g., rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1 // Anand vs Carlsen, 2013"
                      style={{ fontFamily: "'Courier New', Courier, monospace" }}
                    />
                  </Form.Item>

                  <Row gutter={16}>
                    <Col xs={24} sm={12}>
                      <Form.Item name="diagramsPerPage" label="Diagrams per page:" rules={[{ required: true }]}>
                        <InputNumber min={1} style={{ width: '100%' }} />
                      </Form.Item>
                    </Col>
                    <Col xs={24} sm={12}>
                      <Form.Item name="padding" label="Space between diagrams (pt):" rules={[{ required: true }]}>
                        <InputNumber min={0} style={{ width: '100%' }} />
                      </Form.Item>
                    </Col>
                  </Row>

                  <Row gutter={16}>
                    <Col xs={8}>
                      <Form.Item name="lightSquares" label="Light squares">
                        <ColorPicker showText />
                      </Form.Item>
                    </Col>
                    <Col xs={8}>
                      <Form.Item name="darkSquares" label="Dark squares">
                        <ColorPicker showText />
                      </Form.Item>
                    </Col>
                    <Col xs={8}>
                      <Form.Item name="borderColor" label="Border">
                        <ColorPicker showText />
                      </Form.Item>
                    </Col>
                  </Row>
                  
                  <Typography.Text strong>Column Layout Rules</Typography.Text>
                  <Row gutter={16}>
                    <Col span={12}>
                      <Form.Item name="singleColumn" label="Single column if ≤" tooltip="Max diagrams for a single-column layout.">
                        <InputNumber min={1} style={{ width: '100%' }} />
                      </Form.Item>
                    </Col>
                    <Col span={12}>
                      <Form.Item name="twoColumnMax" label="Two columns if ≤" tooltip="Max diagrams for a two-column layout.">
                        <InputNumber min={1} style={{ width: '100%' }} />
                      </Form.Item>
                    </Col>
                  </Row>

                  <Form.Item name="showTurnIndicator" valuePropName="checked" style={{ marginTop: '16px' }}>
                    <Checkbox>Show turn indicator for Black</Checkbox>
                  </Form.Item>

                  <Form.Item name="showPageNumbers" valuePropName="checked" style={{ marginTop: '16px' }}>
                    <Checkbox>Show page numbers</Checkbox>
                  </Form.Item>

                  <Form.Item style={{ marginTop: '24px' }}>
                    <Button type="primary" htmlType="submit" block loading={loading} size="large">
                      Generate PDF
                    </Button>
                  </Form.Item>
                </Form>
              </Spin>
            </Card>
          </Col>
        </Row>
      </Content>
    </Layout>
  );
}

export default App;