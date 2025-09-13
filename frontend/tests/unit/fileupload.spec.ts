import { FileUpload } from '../../src/components/FileUpload';

describe('FileUpload', () => {
  let container: HTMLDivElement;

  beforeEach(() => {
    container = document.createElement('div');
    container.id = 'file-upload-test';
    document.body.appendChild(container);
  });

  afterEach(() => {
    document.body.innerHTML = '';
  });

  test('extractWords parses common delimiters', () => {
    const uploader = new FileUpload('file-upload-test');
    const content = 'BASS,PIANO\nGUITAR;DRUMS\tVIOLIN';
    const words = (uploader as any).extractWords(content);
    expect(words).toEqual(['BASS','PIANO','GUITAR','DRUMS','VIOLIN']);
  });
});
