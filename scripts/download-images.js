const https = require('https');
const fs = require('fs');
const path = require('path');
const sharp = require('sharp');

const DESTINATION_DIR = path.join(__dirname, '..', 'assets', 'destinations');
const MAX_RETRIES = 3;
const RETRY_DELAY = 2000; // 2 seconds

const images = [
    {
        name: 'london.jpg',
        url: 'https://images.unsplash.com/photo-1513635269975-59663e0ac1ad'
    },
    {
        name: 'bangkok.jpg',
        url: 'https://images.unsplash.com/photo-1508009603885-50cf7c579365'
    },
    {
        name: 'paris.jpg',
        url: 'https://images.unsplash.com/photo-1502602898657-3e91760cbb34'
    },
    {
        name: 'tokyo.jpg',
        url: 'https://images.unsplash.com/photo-1540959733332-eab4deabeeaf'
    },
    {
        name: 'seoul.jpg',
        url: 'https://images.unsplash.com/photo-1617541086271-4d43983704bd'
    },
    {
        name: 'dubai.jpg',
        url: 'https://images.unsplash.com/photo-1512453979798-5ea266f8880c'
    },
    {
        name: 'singapore.jpg',
        url: 'https://images.unsplash.com/photo-1525625293386-3f8f99389edd'
    },
    {
        name: 'sydney.jpg',
        url: 'https://images.unsplash.com/photo-1506973035872-a4ec16b8e8d9'
    },
    {
        name: 'london-hotel.jpg',
        url: 'https://images.unsplash.com/photo-1578683010236-d716f9a3f461'
    },
    {
        name: 'sydney-hotel.jpg',
        url: 'https://images.unsplash.com/photo-1571896349842-33c89424de2d'
    },
    {
        name: 'kyoto.jpg',
        url: 'https://images.unsplash.com/photo-1493976040374-85c8e12f0c0e'
    },
    {
        name: 'street-food.jpg',
        url: 'https://images.unsplash.com/photo-1504674900247-0877df9cc836'
    },
    {
        name: 'cherry-blossom.jpg',
        url: 'https://images.unsplash.com/photo-1522383225653-ed111181a951'
    },
    {
        name: 'budget-japan.jpg',
        url: 'https://images.unsplash.com/photo-1480796927426-f609979314bd'
    },
    {
        name: 'mount-fuji.jpg',
        url: 'https://images.unsplash.com/photo-1490806843957-31f4c9a91c65'
    },
    {
        name: 'onsen.jpg',
        url: 'https://images.unsplash.com/photo-1545579133-99bb5ab189b0'
    },
    {
        name: 'shinkansen.jpg',
        url: 'https://images.unsplash.com/photo-1524413840807-0c3cb6fa808d'
    },
    {
        name: 'tokyo-hotel.jpg',
        url: 'https://images.unsplash.com/photo-1542314831-068cd1dbfeeb'
    }
];

// Ensure destination directory exists
if (!fs.existsSync(DESTINATION_DIR)) {
    fs.mkdirSync(DESTINATION_DIR, { recursive: true });
}

function delay(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

async function downloadAndOptimizeImage(imageUrl, outputPath, retryCount = 0) {
    return new Promise((resolve, reject) => {
        https.get(imageUrl, async (response) => {
            if (response.statusCode !== 200) {
                const error = new Error(`Failed to download: ${response.statusCode}`);
                if (retryCount < MAX_RETRIES) {
                    console.log(`⚠️ Retry ${retryCount + 1}/${MAX_RETRIES} for ${path.basename(outputPath)}`);
                    await delay(RETRY_DELAY);
                    return resolve(downloadAndOptimizeImage(imageUrl, outputPath, retryCount + 1));
                }
                return reject(error);
            }

            const chunks = [];
            
            response.on('data', (chunk) => chunks.push(chunk));
            
            response.on('end', async () => {
                const buffer = Buffer.concat(chunks);
                try {
                    // Process with Sharp
                    await sharp(buffer)
                        .resize(1200, 800, {
                            fit: 'cover',
                            position: 'attention', // Use attention-based cropping
                            withoutEnlargement: true
                        })
                        .jpeg({
                            quality: 85,
                            progressive: true,
                            mozjpeg: true, // Use mozjpeg for better compression
                            chromaSubsampling: '4:4:4' // Better color quality
                        })
                        .toFile(outputPath);
                    
                    console.log(`✅ Successfully processed: ${path.basename(outputPath)}`);
                    resolve();
                } catch (error) {
                    console.error(`❌ Error processing ${path.basename(outputPath)}:`, error);
                    if (retryCount < MAX_RETRIES) {
                        console.log(`⚠️ Retry ${retryCount + 1}/${MAX_RETRIES} for ${path.basename(outputPath)}`);
                        await delay(RETRY_DELAY);
                        return resolve(downloadAndOptimizeImage(imageUrl, outputPath, retryCount + 1));
                    }
                    reject(error);
                }
            });
        }).on('error', async (error) => {
            console.error(`❌ Error downloading ${path.basename(outputPath)}:`, error);
            if (retryCount < MAX_RETRIES) {
                console.log(`⚠️ Retry ${retryCount + 1}/${MAX_RETRIES} for ${path.basename(outputPath)}`);
                await delay(RETRY_DELAY);
                return resolve(downloadAndOptimizeImage(imageUrl, outputPath, retryCount + 1));
            }
            reject(error);
        });
    });
}

async function downloadAllImages() {
    console.log('🚀 Starting image downloads and optimization...');
    
    const results = {
        success: [],
        failed: []
    };
    
    for (const image of images) {
        const outputPath = path.join(DESTINATION_DIR, image.name);
        console.log(`📥 Processing ${image.name}...`);
        
        try {
            await downloadAndOptimizeImage(image.url, outputPath);
            results.success.push(image.name);
        } catch (error) {
            console.error(`Failed to process ${image.name}`);
            results.failed.push(image.name);
        }
    }
    
    console.log('\n📊 Summary:');
    console.log(`✅ Successfully processed: ${results.success.length} images`);
    if (results.failed.length > 0) {
        console.log(`❌ Failed to process: ${results.failed.length} images`);
        console.log('Failed images:', results.failed.join(', '));
    }
    console.log('✨ Process completed!');
}

downloadAllImages(); 