import React, { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';
import axios from 'axios';

const App: React.FC = () => {
    const [preview, setPreview] = useState('');
    const [result, setResult] = useState('');

    const onDrop = useCallback(async (acceptedFiles: any[]) => {
        try {
            const file = acceptedFiles[0];
            setPreview(URL.createObjectURL(file));
            const formData = new FormData();
            formData.append('image', file);
            const res = await axios.post(
                'http://127.0.0.1:5000/colorize',
                formData,
                {
                    headers: {
                        'Content-Type': 'multipart/form-data'
                    },
                    responseType: 'blob'
                }
            );
            setResult(URL.createObjectURL(res.data));
        } catch (error) {
            alert('Something went wrong');
            console.error(error);
        }
    }, []);
    const { getRootProps, getInputProps, isDragActive } = useDropzone({
        onDrop
    });

    return (
        <div>
            <h1>SAR</h1>
            <main style={{ display: 'flex', gap: '10px' }}>
                {!preview ? (
                    <div
                        {...getRootProps()}
                        style={{ border: '1px dashed black', padding: '10px' }}
                    >
                        <input {...getInputProps()} />
                        {isDragActive ? (
                            <p>Drop the files here ...</p>
                        ) : (
                            <p>
                                Drag 'n' drop some files here, or click to
                                select files
                            </p>
                        )}
                    </div>
                ) : (
                    <div>
                        <img
                            src={preview}
                            style={{ objectFit: 'contain' }}
                            alt="Preview Image"
                            height={256}
                            width={256}
                        />
                    </div>
                )}
                {result && (
                    <img
                        src={result}
                        style={{ objectFit: 'contain' }}
                        alt="Result Image"
                        height={256}
                        width={256}
                    />
                )}
            </main>
        </div>
    );
};

export default App;
